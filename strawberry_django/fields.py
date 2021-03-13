import strawberry
from typing import Callable, List, Optional
import dataclasses
from . import utils

@dataclasses.dataclass
class RelationResolver:
    resolver: Optional[Callable]
    related_name: Optional[str]

    def __post_init__(self):
        if self.resolver:
            self.resolver_func.__annotations__.update(self.resolver.__annotations__)

    def resolver_func(self, root, info, filters: Optional[List[str]] = []):
        related_name = self.related_name
        if related_name is None:
            related_name = info.field_name
        manager = getattr(root, related_name)
        filter, exclude = utils.process_filters(filters)
        qs = manager.filter(**filter).exclude(**exclude)
        if self.resolver:
            qs = self.resolver(root, info, qs)
        return qs


def field(resolver=None, **kwargs):
    field = strawberry.field(resolver, **kwargs)
    # workaround for forward reference resolution issue
    field._field_definition.origin = None
    return field


def relation_field(resolver=None, *, related_name=None, **kwargs):
    relation_resolver = RelationResolver(resolver, related_name)
    resolver_func = relation_resolver.resolver_func
    return field(resolver_func)
