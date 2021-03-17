from django.db.models import fields
from typing import List, Optional
import datetime, decimal, uuid
import dataclasses
import strawberry
from . import utils


field_type_map = {
    fields.AutoField: strawberry.ID,
    fields.BigAutoField: strawberry.ID,
    fields.BigIntegerField: int,
    fields.BooleanField: bool,
    fields.CharField: str,
    fields.DateField: datetime.date,
    fields.DateTimeField: datetime.datetime,
    fields.DecimalField: decimal.Decimal,
    fields.EmailField: str,
    #TODO: fields.FieldFile
    fields.FilePathField: str,
    fields.FloatField: float,
    #TODO: fields.ImageField
    fields.GenericIPAddressField: str,
    fields.IntegerField: int,
    #TODO: fields.JSONField
    fields.NullBooleanField: Optional[bool],
    fields.PositiveBigIntegerField: int,
    fields.PositiveIntegerField: int,
    fields.PositiveSmallIntegerField: int,
    fields.SlugField: str,
    fields.SmallAutoField: strawberry.ID,
    fields.SmallIntegerField: int,
    fields.TextField: str,
    fields.TimeField: datetime.time,
    fields.URLField: str,
    fields.UUIDField: uuid.UUID,
}


class LazyModelType(strawberry.LazyType):
    def __init__(self, field, types):
        self.field, self.types = field, types
        super().__init__(None, None, None)

    def resolve_type(self):
        model = self.field.related_model
        if model not in self.types:
            db_field_type = type(self.field)
            raise TypeError(f"No type defined for field '{db_field_type.__name__}'"
                    f" which has related model '{model._meta.object_name}'")
        return self.types[model]


def get_field_type(field, field_types):
    if field.name in field_types:
        return field_types[field.name]

    db_field_type = type(field)
    if db_field_type in field_types:
        return field_types[db_field_type]

    if field.is_relation:
        model = field.related_model
        if model in field_types:
            return field_types[model]
        # TODO: show field name
        raise TypeError(f"No type defined for field '{db_field_type.__name__}'"
                f" which has related model '{model._meta.object_name}'")

    field_type = field_type_map.get(db_field_type)
    if field_type is None:
        # TODO: show field name
        raise TypeError(f"No type defined for '{db_field_type.__name__}'")
    return field_type


def is_optional(field, is_input, is_update):
    if is_input:
        has_default = field.default != fields.NOT_PROVIDED
        if field.blank or is_update or has_default:
            return True
    if field.null:
        return True
    return False

def is_in(item, item_list, default=False):
    if not item_list:
        return default
    return item in item_list


def process_fields(fields, types, model):
    field_names = []
    field_types = {}

    if types:
        field_types.update(types)

    if fields is None:
        return field_names, field_types

    model_field_names = [field.name for field in model._meta.get_fields()]

    for field in fields:
        if isinstance(field, str):
            field_name = field
        elif isinstance(field, tuple):
            if len(field) != 2:
                raise TypeError('Length of tuple should exactly 2')
            field_name, field_type = field
            field_types[field_name] = field_type
        else:
            raise TypeError('Type of field parameter should be str or tuple')
        if field_name not in model_field_names:
            raise AttributeError(f"Django model '{model._meta.object_name}' has no field '{field_name}'")
        field_names.append(field_name)
    return field_names, field_types

from .fields import (
    field as strawberry_django_field,
    relation_field as strawberry_django_relation_field,
)


def get_model_fields(cls, model, fields, types, is_input, is_update):
    field_names, field_types = process_fields(fields, types, model)

    model_fields = []
    for field in model._meta.get_fields():
        if not is_in(field.name, field_names, default=True):
            continue

        try:
            field_type = get_field_type(field, field_types)
        except TypeError:
            if not field.is_relation or types is None:
                raise
            field_type = LazyModelType(field, types)

        if field.is_relation:
            if field.many_to_many or field.one_to_many:
                field_type = List[field_type]

        if field.one_to_many or field.many_to_many:
            field_value = strawberry_django_relation_field()
        else:
            field_value = strawberry_django_relation_field(m2m=False)

        if is_optional(field, is_input, is_update):
            field_type = Optional[field_type]

        model_fields.append((field.name, field_type, field_value))
    return model_fields


