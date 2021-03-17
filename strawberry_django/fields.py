import strawberry
from typing import Callable, List, Optional
import dataclasses
from . import resolvers, utils

def field(resolver=None, **kwargs):
    if resolver:
        resolver = resolvers.DjangoResolver(resolver)
    field = strawberry.field(resolver, **kwargs)
    # workaround for forward reference resolution issue
    field._field_definition.origin = None
    return field

#TODO: better name for m2m parameter
def relation_field(resolver=None, *, related_name=None, m2m=True, **kwargs):
    if m2m:
        resolver = resolvers.get_relation_resolver_m2m(resolver, related_name)
    else:
        resolver = resolvers.get_relation_resolver(resolver, related_name)
    return field(resolver, **kwargs)
