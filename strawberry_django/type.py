import strawberry
from .types import get_model_fields


def type(model, *, fields=None, types=None, is_update=False, **kwargs):
    def wrapper(cls):
        is_input = kwargs.get('is_input', False)
        model_fields = get_model_fields(cls, model, fields, types, is_input, is_update)
        if not hasattr(cls, '__annotations__'):
            cls.__annotations__ = {}
        for field_name, field_type, field_value in model_fields:
            cls.__annotations__[field_name] = field_type
            if field_value is not None:
                setattr(cls, field_name, field_value)
        cls._django_model = model
        return strawberry.type(cls, **kwargs)
    return wrapper


def input(model, *, fields=None, types=None, is_update=False, **kwargs):
    return type(model, fields=fields, types=types, is_update=is_update, is_input=True, **kwargs)
