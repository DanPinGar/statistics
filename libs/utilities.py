import os
import pickle
import json
import yaml


def load_json(path):
    with open(path,'r') as file:
        data = json.load(file)
    return data


def save_json(data,path):
    with open(path ,'w') as file:
        json.dump(data, file,indent=4)


def load_peakle(path):
    with open(path,'rb') as file:
        data = pickle.load(file)
    return data


def save_peakle(data,path):
    with open(path,'wb') as file:
        pickle.dump(data,file)
    

def remove_file(file_path):
    if os.path.isfile(file_path):
        os.remove(file_path)


def load_yaml(path):
    with open(path,'r') as file:
        data = yaml.safe_load(file)
    return data

