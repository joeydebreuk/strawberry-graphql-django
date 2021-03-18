import datetime, decimal, uuid
import pytest
import strawberry
import strawberry_django
import typing
from django.db import models
from .models import User


class FieldTypesModel(models.Model):
    boolean = models.BooleanField()
    char = models.CharField(max_length=50)
    date = models.DateField()
    date_time = models.DateTimeField()
    decimal = models.DecimalField()
    email = models.EmailField()
    file_path = models.FilePathField()
    float = models.FloatField()
    generic_ip_address = models.GenericIPAddressField()
    integer = models.IntegerField()
    null_boolean = models.NullBooleanField()
    positive_big_integer = models.PositiveBigIntegerField()
    positive_integer = models.PositiveIntegerField()
    positive_small_integer = models.PositiveSmallIntegerField()
    slug = models.SlugField()
    small_integer = models.SmallIntegerField()
    text = models.TextField()
    time = models.TimeField()
    url = models.URLField()
    uuid = models.UUIDField()


def test_field_types():
    @strawberry_django.type(FieldTypesModel)
    class Type:
        pass

    assert [(f.name, f.type) for f in Type._type_definition.fields] == [
        ('id', strawberry.ID),
        ('boolean', bool),
        ('char', str),
        ('date', datetime.date),
        ('dateTime', datetime.datetime),
        ('decimal', decimal.Decimal),
        ('email', str),
        ('filePath', str),
        ('float', float),
        ('genericIpAddress', str),
        ('integer', int),
        ('nullBoolean', bool),
        ('positiveBigInteger', int),
        ('positiveInteger', int),
        ('positiveSmallInteger', int),
        ('slug', str),
        ('smallInteger', int),
        ('text', str),
        ('time', datetime.time),
        ('url', str),
        ('uuid', uuid.UUID),
    ]


def test_subset_of_fields():
    @strawberry_django.type(FieldTypesModel, fields=['id', 'integer', 'text'])
    class Type:
        pass

    assert [(f.name, f.type) for f in Type._type_definition.fields] == [
        ('id', strawberry.ID),
        ('integer', int),
        ('text', str),
    ]


def test_type_extension():
    @strawberry_django.type(FieldTypesModel, fields=['char'])
    class Type:
        text: bytes # override type
        @strawberry.field
        def my_field() -> int:
            return 0

    assert [(f.name, f.type) for f in Type._type_definition.fields] == [
        ('text', bytes),
        ('char', str),
        ('myField', int),
    ]


def test_field_does_not_exist():
    with pytest.raises(AttributeError, match="Django model 'FieldTypesModel' has no field 'unknownField'"):
        @strawberry_django.type(FieldTypesModel, fields=['unknownField'])
        class Type:
            pass


class OptionalFieldsModel(models.Model):
    mandatory = models.IntegerField()
    default = models.IntegerField(default=1)
    blank = models.IntegerField(blank=True)
    null = models.IntegerField(null=True)
    null_boolean = models.NullBooleanField()


def test_input_type():
    @strawberry_django.input(OptionalFieldsModel)
    class InputType:
        pass

    assert [(f.name, f.type, f.is_optional) for f in InputType._type_definition.fields] == [
        ('id', strawberry.ID, True),
        ('mandatory', int, False),
        ('default', int , True),
        ('blank', int, True),
        ('null', int, True),
        ('nullBoolean', bool, True),
    ]


def test_input_type_for_partial_update():
    @strawberry_django.input(OptionalFieldsModel, is_update=True)
    class InputType:
        pass

    assert [(f.name, f.type, f.is_optional) for f in InputType._type_definition.fields] == [
        ('id', strawberry.ID, True),
        ('mandatory', int, True),
        ('default', int , True),
        ('blank', int, True),
        ('null', int, True),
        ('nullBoolean', bool, True),
    ]


def test_forward_reference():
    global MyBytes

    class ForwardReferenceModel(models.Model):
        string = models.CharField(max_length=50)
        bytes1 = models.CharField(max_length=50)
        bytes2 = models.CharField(max_length=50)

    @strawberry_django.type(ForwardReferenceModel, fields=[
        'string',
        ('bytes1', bytes),
        ('bytes2', 'MyBytes'),
    ])
    class Type:
        bytes0: 'MyBytes'

    class MyBytes(bytes):
        pass

    assert [(f.name, f.type) for f in Type._type_definition.fields] == [
        ('bytes0', MyBytes),
        ('string', str),
        ('bytes1', bytes),
        ('bytes2', MyBytes),
    ]

    del MyBytes


def test_type_instance():
    @strawberry_django.type(User, fields=['id', 'name'])
    class UserType:
        pass
    user = UserType(1, 'user')
    assert user.id == 1
    assert user.name == 'user'


def test_input_instance():
    @strawberry_django.input(User, fields=['id', 'name'])
    class InputType:
        pass
    user = InputType(1, 'user')
    assert user.id == 1
    assert user.name == 'user'
