import strawberry
from typing import Callable, List, Optional, Dict
import dataclasses
from . import utils, queries

@dataclasses.dataclass
class DjangoField:
    resolver: Callable
    source: Optional[str]
    kwargs: dict

    def resolve(self, is_relation, is_m2m):
        resolver = queries.resolvers.get_resolver(self.resolver, self.source, is_relation, is_m2m)
        field = strawberry.field(resolver, **self.kwargs)
        # workaround for forward reference resolution issue
        field._field_definition.origin = None
        return field


def field(resolver=None, source=None, **kwargs):
    return DjangoField(resolver, source, kwargs)

mutation = field
