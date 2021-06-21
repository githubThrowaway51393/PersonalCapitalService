import json
from os import listdir
from os.path import isfile, join

IGNORE_PATH='./ignores/'

def read_file_into_list(path):
    list = []
    with open(path, 'r') as data_file:
            lines = data_file.read().splitlines()
            return(lines)
            
def read_file_as_string(path):
    with open(path, 'r') as data_file:
        lines = data_file.read()
        return(lines)
           
def read_json_file(path):
    with open(path) as data_file:
        data = json.load(data_file)
        return data
        
def write_json_to_file(path, new_json):
    f = open(path, "w")
    f.write(new_json)
    f.close()
        
def read_ignore_file_into_list(name):
    return read_file_into_list(IGNORE_PATH+name)
    
def read_all_files_to_list(path):
    return [f for f in listdir(path) if isfile(join(path, f))]