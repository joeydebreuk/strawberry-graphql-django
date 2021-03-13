import strawberry
from django.db.models import fields
import ast

def parse_value(value):
    try:
        return ast.literal_eval(value)
    except ValueError:
        raise ValueError('Invalid filter value')

def process_filters(filters):
    filter, exclude = {}, {}
    for string in filters:
        try:
            k, v = string.split('=', 1)
        except ValueError:
            raise ValueError(f'Invalid filter "{filter}"')
        if '!' in k:
            k = k.strip('!')
            exclude[k] = parse_value(v)
        else:
            filter[k] = parse_value(v)
    return filter, exclude

def get_input_data(model, data):
    values = {}
    for field in model._meta.fields:
        field_name = field.attname
        value = getattr(data, field_name, strawberry.arguments.UNSET)
        if value is strawberry.arguments.UNSET:
            continue
        values[field_name] = value
    return values

def camel_to_snake(s):
    return ''.join(['_'+c.lower() if c.isupper() else c for c in s]).lstrip('_')
