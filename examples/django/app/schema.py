from typing import Optional
import strawberry
import strawberry_django
from . import models

# types are generated with selected fields from models
@strawberry_django.type(models.User, fields=['id', 'name'])
class MyUser:
    # types can be extended
    @strawberry.field
    def name_upper(root) -> str:
        return root.name.upper()

    # forward referensing works fine
    group: Optional['Group'] = strawberry_django.field()

    # relation field name is configurable
    user_group: Optional['Group'] = strawberry_django.field(field_name='group')


# type register is used as a type store which is then
# used to resolve types of relation fields
types = strawberry_django.TypeRegister()

@types.register
@strawberry_django.type(models.User, types=types)
class User:
    pass

@types.register
@strawberry_django.type(models.Group, types=types)
class Group:
    pass

@types.register
@strawberry_django.type(models.Tag, types=types)
class Tag:
    pass

# input types
@types.register
@strawberry_django.input(models.User, types=types)
class UserInput:
    pass

@types.register
@strawberry_django.input(models.Group, types=types)
class GroupInput:
    pass

@types.register
@strawberry_django.input(models.Tag, types=types)
class TagInput:
    pass

# queries can be auto generated from types
GeneratedQuery = strawberry_django.queries(User, Group, Tag, types=types)
GeneratedMutations = strawberry_django.mutations(User, Group, Tag, types=types)

@strawberry.type
class Query(GeneratedQuery):
    @strawberry.field
    @strawberry_django.django_resolver
    def my_user(name: str) -> MyUser:
        return models.User.objects.get(name=name)


schema = strawberry.Schema(query=Query, mutation=GeneratedMutations)
