from typing import List, Optional
import strawberry
from . import resolvers
from .. import utils

def queries(*types):
    query_fields = {}
    for object_type in types:
        model = object_type._django_model
        object_name = utils.camel_to_snake(model._meta.object_name)
        query_fields[f'{object_name}'] = resolvers.get_object_resolver(model, object_type)
        query_fields[f'{object_name}s'] = resolvers.get_list_resolver(model, object_type)
    return strawberry.type(type('Query', (), query_fields))

queries.get = resolvers.get_object_resolver
queries.list = resolvers.get_list_resolver
