import json
from itertools import product


import pytest
from jsonschema.validators import Draft4Validator

from tests.constants import CONTENT_TYPES
from tests.utils import get_data_for, flatten_list, get_schemas_for


class TestSchemas:

    schemas = get_schemas_for(*CONTENT_TYPES.as_list)

    @pytest.mark.parametrize(
        "content_type,data", flatten_list(
            [list(product([ct, ], d)) for ct, d in get_data_for(*CONTENT_TYPES.as_list).items()]
        )
    )
    def test_schema(self, content_type, data):
        schema = self.schemas[content_type]
        v = Draft4Validator(schema)
        errors = [f"{'.'.join(error.path)} -> {error.message}" for error in v.iter_errors(data)]
        if errors:
            model = f"<{content_type.capitalize()}>"
            if 'id' in data:
                model = f"<{content_type.capitalize()} id={data['id']}>"
            elif 'name' in data:
                model = f"<{content_type.capitalize()} id={data['name']}>"
            errors_text = '\n\t- '.join(errors)
            pytest.fail(f'{model}\n{json.dumps(data, indent=2)}\nError(s): \n\t- {errors_text}')
