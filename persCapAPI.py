from personalcapital import PersonalCapital, RequireTwoFactorException, TwoFactorVerificationModeEnum
import getpass
import json
import logging
import os
import sys
from datetime import datetime, timedelta
from cryptography.fernet import Fernet
from jsonutils import *
from dateutils import *
from encryptor import *
from stringutils import *
from fileio import *
from multipledispatch import dispatch

CREDS_FILE_PATH="./creds.json"
  
# Python 2 and 3 compatibility
if hasattr(__builtins__, 'raw_input'):
    input = raw_input


class Credentials():
    email = ""
    password = ""
    def __init__(self, e, p):
        self.email = e
        self.password = p

class PewCapital(PersonalCapital):
    """
    Extends PersonalCapital to save and load session
    So that it doesn't require 2-factor auth every time
    """
    c = None
    cat_map = {}

    def __init__(self):
        PersonalCapital.__init__(self)
        self.__session_file = 'session.json'
        self.c = get_creds_from_file()

    def load_session(self):
        try:
            with open(self.__session_file) as data_file:    
                cookies = {}
                try:
                    cookies = json.load(data_file)
                except ValueError as err:
                    logging.error(err)
                self.set_session(cookies)
        except IOError as err:
            logging.error(err)

    def save_session(self):
        print("Saving Session")
        with open(self.__session_file, 'w') as data_file:
            data_file.write(json.dumps(self.get_session()))
    
    def refresh_session(self):
        try:
            self.login(self.c.email, self.c.password)
        except RequireTwoFactorException:
            self.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
            self.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, input('code: '))
            self.authenticate_password(self.c.password)
    
        self.save_session()
      
    def get_category_map(self):
        res = self.fetch('/transactioncategory/getCategories')
        cat_list = []
        for item in res.json()['spData']:
            singular = {
                "id":item['transactionCategoryId'],
                "name":item['name'],
                "type":item['type']
            }
            cat_list.append(singular)
        cats = {
            "categories":cat_list
        }
        self.cat_map = cats

def setup_login():
    #email, password = get_email(), get_password()
    pc = PewCapital()
    pc.load_session()

    try:
        pc.login(pc.c.email, pc.c.password)
    except RequireTwoFactorException:
        pc.two_factor_challenge(TwoFactorVerificationModeEnum.SMS)
        pc.two_factor_authenticate(TwoFactorVerificationModeEnum.SMS, input('code: '))
        pc.authenticate_password(pc.c.password)
        pc.save_session()
    
    pc.get_category_map()
        
    return pc

    
def get_creds_from_file():
    creds_json = read_json_file(CREDS_FILE_PATH)
    return Credentials(decrypt_text(creds_json['user']), decrypt_text(creds_json['pass']))
    
def main():
    pc = setup_login()
    pc.save_session()
    print("test")
    
if __name__ == '__main__':
    main()
