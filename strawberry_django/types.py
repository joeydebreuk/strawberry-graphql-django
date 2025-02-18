from django.db.models import fields
from strawberry.arguments import UNSET
from typing import get_origin, List, Optional
import dataclasses
import datetime, decimal, uuid
import strawberry
from . import utils
from .fields import DjangoField, field as strawberry_django_field


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
    def __init__(self, field, type_register, is_input):
        self.field, self.type_register, self.is_input = field, type_register, is_input
        super().__init__(field.name, None, None)

    def resolve_type(self):
        model = self.field.related_model

        field_type = self.type_register.get(model, self.is_input, UNSET)
        if field_type is not UNSET:
            return field_type

        db_field_type = type(self.field)
        raise TypeError(f"No type defined for field '{db_field_type.__name__}'"
                f" which has related model '{model._meta.object_name}'")


def get_field_type(field, type_register, is_input):
    db_field_type = type(field)

    if type_register:
        field_type = type_register.get(field.name, is_input, UNSET)
        if field_type is not UNSET:
            return field_type

        field_type = type_register.get(db_field_type, is_input, UNSET)
        if field_type is not UNSET:
            return field_type

        if field.is_relation:
            model = field.related_model

            field_type = type_register.get(model, is_input, UNSET)
            if field_type is not UNSET:
                return field_type

            # TODO: show field name
            raise TypeError(f"No type defined for field '{db_field_type.__name__}'"
                    f" which has related model '{model._meta.object_name}'")

    field_type = field_type_map.get(db_field_type, UNSET)
    if field_type is not UNSET:
        return field_type

    if field.is_relation:
        model = field.related_model
        raise TypeError(f"No type defined for Django model '{model._meta.object_name}'")

    # TODO: show field name
    raise TypeError(f"No type defined for '{db_field_type.__name__}'")


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


def process_fields(fields, model):
    field_names = []

    if fields is None:
        return field_names

    model_field_names = [field.name for field in model._meta.get_fields()]

    for field in fields:
        if isinstance(field, str):
            field_name = field
        else:
            raise TypeError('Type of field parameter should be str')
        if field_name not in model_field_names:
            raise AttributeError(f"Django model '{model._meta.object_name}' has no field '{field_name}'")
        field_names.append(field_name)
    return field_names


def get_model_fields(cls, model, fields, types, is_input, is_update):
    if fields == []:
        return []

    field_names = process_fields(fields,  model)
    type_register = types

    model_fields = []
    for field in model._meta.get_fields():
        if not is_in(field.name, field_names, default=True):
            continue

        if is_input:
            if not field.editable:
                continue

            if field.is_relation:
                if field.many_to_many or field.one_to_many:
                    field_type = Optional[List[strawberry.ID]]
                    field_value = strawberry.arguments.UNSET
                    model_fields.extend([
                        (f'{field.name}_add', field_type, field_value),
                        (f'{field.name}_set', field_type, field_value),
                        (f'{field.name}_remove', field_type, field_value),
                    ])
                else:
                    field_name = field.attname
                    field_type = strawberry.ID
                    if is_optional(field, is_input, is_update):
                        field_type = Optional[field_type]
                    model_fields.append((field_name, field_type, None))
                continue

        try:
            field_type = get_field_type(field, type_register, is_input)
        except TypeError:
            if not field.is_relation or type_register is None:
                raise
            field_type = LazyModelType(field, type_register, is_input)

        if field.is_relation:
            if field.many_to_many or field.one_to_many:
                field_type = List[field_type]
            field_value = strawberry_django_field(field_name=field.name)
        else:
            field_value = strawberry.arguments.UNSET

        if is_optional(field, is_input, is_update):
            field_type = Optional[field_type]

        model_fields.append((field.name, field_type, field_value))
    return model_fields


# post processing fields before passing them to strawberry
def update_fields(cls, model):
    for field_name, field in cls.__dict__.items():
        if not isinstance(field, DjangoField):
            continue

        django_field_name = field.field_name or field_name
        django_field = model._meta.get_field(django_field_name)
        is_m2m = django_field.many_to_many or django_field.one_to_many

        field = field.resolve(django_field.is_relation, is_m2m)
        setattr(cls, field_name, field)
