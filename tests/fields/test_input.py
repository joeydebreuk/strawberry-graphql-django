import strawberry
import strawberry_django
from django.db import models


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

