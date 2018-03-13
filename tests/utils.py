import json
from os import path

import jsonref


def get_schema(content_type):
    absolute_path = path.abspath(path.join(path.dirname(__file__), f'../schemas/{content_type}.json'))
    base_uri = f'file://{path.dirname(absolute_path)}/'

    with open(absolute_path, 'r') as file_object:
        schema = jsonref.loads(file_object.read(), base_uri=base_uri, jsonschema=True)

    return schema


def get_data(content_type):
    absolute_path = path.abspath(path.join(path.dirname(__file__), f'../data/{content_type}.json'))
    with open(absolute_path, 'r') as file_object:
        data = json.load(file_object)
    return data


def get_schemas_for(*content_types):
    schemas = {}
    for ct in content_types:
        schemas[ct] = get_schema(ct)
    return schemas


def get_data_for(*content_types):
    data = {}
    for ct in content_types:
        data[ct] = get_data(ct)
    return data


def flatten_list(l):
    return [item for sublist in l for item in sublist]
