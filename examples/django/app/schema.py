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
    group: 'Group' = strawberry_django.relation_field()


# type register can be used as a type store which is then
# used to resolve types of relation fields
types = strawberry_django.TypeRegister()

@types.register
@strawberry_django.type(models.Tag, types=types)
class Tag:
    pass

@types.register
@strawberry_django.type(models.Group, types=types)
class Group:
    pass

@types.register
@strawberry_django.type(models.User, types=types)
class User:
    pass


# queries can be auto generated from types
GeneratedQuery = strawberry_django.queries(User, Group, Tag)

@strawberry.type
class Query(GeneratedQuery):
    @strawberry.field
    def my_user(name: str) -> MyUser:
        return models.User.get(name=name)


schema = strawberry.Schema(query=Query)
