import json
from os import path


def get_data(content_type):
    absolute_path = path.abspath(path.join(path.dirname(__file__), f'../data/{content_type}.json'))
    with open(absolute_path, 'r') as file_object:
        data = json.load(file_object)
    return data


def get_data_for(*content_types):
    data = {}
    for ct in content_types:
        data[ct] = get_data(ct)
    return data


def flatten_list(l):
    return [item for sublist in l for item in sublist]
