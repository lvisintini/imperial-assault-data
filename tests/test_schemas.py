import json
from os import path
from itertools import product

import jsonref
import pytest
from jsonschema.validators import Draft4Validator

from tests.constants import CONTENT_TYPES
from tests.utils import get_data_for, flatten_list


class TestSchemas:
    @staticmethod
    def get_schema(content_type):
        absolute_path = path.abspath(path.join(path.dirname(__file__), f'../schemas/{content_type}.json'))
        base_uri = f'file://{path.dirname(absolute_path)}/'

        with open(absolute_path, 'r') as file_object:
            schema = jsonref.loads(file_object.read(), base_uri=base_uri, jsonschema=True)

        return schema

    @pytest.mark.parametrize(
        "content_type,data", flatten_list(
            [list(product([ct, ], d)) for ct, d in get_data_for(*CONTENT_TYPES.as_list).items()]
        )
    )
    def test_schema(self, content_type, data):
        schema = self.get_schema(content_type)
        v = Draft4Validator(schema)
        errors = [error.message for error in v.iter_errors(data)]
        if errors:
            model = f"<{content_type.capitalize()}>"
            if 'id' in data:
                model = f"<{content_type.capitalize()} id={data['id']}>"
            elif 'name' in data:
                model = f"<{content_type.capitalize()} id={data['name']}>"
            errors_text = '\n\t- '.join(errors)
            pytest.fail(f'{model}\n{json.dumps(data, indent=2)}\nError(s): \n\t- {errors_text}')
