from typing import List, Optional
import strawberry
from . import utils

def get_object_resolver(model, object_type):
    def resolver(id: strawberry.ID) -> object_type:
        obj = model.objects.get(id=id)
        return obj
    return resolver

def get_list_resolver(model, object_type):
    def resolver(filters: Optional[List[str]] = []) -> List[object_type]:
        qs = model.objects.all()
        filter, exclude = utils.process_filters(filters)
        qs = qs.filter(**filter).exclude(**exclude)
        return qs
    return resolver

def queries(*types):
    fields = {}
    for object_type in types:
        model = object_type._django_model
        object_name = utils.camel_to_snake(model._meta.object_name)
        fields[f'{object_name}'] = strawberry.field(get_object_resolver(model, object_type))
        fields[f'{object_name}s'] = strawberry.field(get_list_resolver(model, object_type))
    return strawberry.type(type('Query', (), fields))
