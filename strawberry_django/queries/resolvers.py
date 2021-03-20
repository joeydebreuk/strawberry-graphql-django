from asgiref.sync import sync_to_async
from django.db import models
from strawberry.types.fields.resolver import StrawberryResolver
from typing import List, Optional
import strawberry
from .. import fields, hooks, utils
from .arguments import resolve_type_args


class DjangoResolver(StrawberryResolver):
    def __call__(self, *args, **kwargs):
        f = super().__call__
        def func(*args, **kwargs):
            result = f(*args, **kwargs)
            if isinstance(result, models.QuerySet):
                result = list(result)
            return result
        if utils.is_async():
            func = sync_to_async(func, thread_sensitive=True)
        return func(*args, **kwargs)


def get_object_resolver(*args, types=None):
    model, object_type = resolve_type_args(args, types=types, single=True)
    @fields.field
    def resolver(id: strawberry.ID) -> object_type:
        obj = model.objects.get(id=id)
        return obj
    return resolver


def get_list_resolver(*args, types=None, queryset=None):
    model, object_type = resolve_type_args(args, types=types, single=True)
    @hooks.add(queryset=queryset)
    @fields.field
    def resolver(info, filters: Optional[List[str]] = [], order_by: Optional[List[str]] = []) -> List[object_type]:
        class context:
            qs = model.objects.all()
        if filters:
            filter, exclude = utils.process_filters(filters)
            context.qs = context.qs.filter(**filter).exclude(**exclude)
        if order_by:
            context.qs = context.qs.order_by(*order_by)
        def queryset(hook):
            context.qs = hook(info=info, qs=context.qs)
        resolver._call_hooks('queryset', queryset)
        return context.qs
    return resolver


def get_relation_resolver(resolver, related_name):
    def func(root, info):
        related_name = func.related_name
        if related_name is None:
            related_name = info.field_name
        obj = getattr(root, related_name)
        return obj
    func.resolver = resolver
    func.related_name = related_name
    return func


def get_relation_resolver_m2m(resolver, related_name):
    def func(root, info, filters: Optional[List[str]] = [], order_by: Optional[List[str]] = []):
        related_name = func.related_name
        if related_name is None:
            related_name = info.field_name
        manager = getattr(root, related_name)
        qs = manager.all()
        if filters:
            filter, exclude = utils.process_filters(filters)
            qs = qs.filter(**filter).exclude(**exclude)
        if order_by:
            qs = qs.order_by(*order_by)
        if func.resolver:
            qs = func.resolver(root, info, qs)
        return qs
    func.resolver = resolver
    func.related_name = related_name
    return func
