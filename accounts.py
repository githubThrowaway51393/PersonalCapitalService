from persCapAPI import *
from jsonutils import *
from dateutils import *
from encryptor import *
from stringutils import *
from fileio import *

def get_account_values_as_json(pc):
    res = pc.fetch('/newaccount/getAccounts')
    accs = []
    for acc in res.json()['spData']['accounts']:
        singular = {
            "name":decode_utf8(acc['name']),
            "balance":acc['balance'] 
        }
        accs.append(singular)
    accjson = {
        "networth":res.json()['spData']['networth'],
        "accounts":accs
    }
    return return_as_json(accjson)
    
def get_account_values_new_as_json(pc):
    res = pc.fetch('/newaccount/getAccounts2')
    accs = []
    for acc in res.json()['spData']['accounts']:
        singular = {
            "name":decode_utf8(acc['name']),
            "balance":acc['balance'],
            "accountType" : acc.get('accountTypeNew'),
            "accountSubtype" : acc.get('accountTypeSubtype'),
            "firmName" : acc.get('firmName')
        }
        accs.append(singular)
    accjson = {
        "networth":res.json()['spData']['networth'],
        "accounts":accs
    }
    return accjson
    
def get_clean_account_type_from_account(account):
    accTypeMain = account['accountType']
    accTypeSub = account['accountSubtype']
    if(accTypeSub is None):
        accTypeSub = ""
    else:
        accTypeSub = " - " + accTypeSub
    if(accTypeMain is None):
        accTypeMain = ""
    return accTypeMain + accTypeSub
    
def get_account_from_accounts(accounts, name):
    accounts = accounts['accounts'] 
    for acc in accounts:
        if(acc['name'] == name):
            return acc
    return None