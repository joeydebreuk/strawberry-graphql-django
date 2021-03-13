import strawberry_django
from . import models

@strawberry_django.type(models.User, fields=[
    'id',
    'name',
    ('group', 'Group'),
    ('tag', 'Tag'),
])
class User:
    pass

@strawberry_django.type(models.Group, fields=[
    'id',
    'name',
    ('users', 'User'),
    ('tags', 'Tag'),
])
class Group:
    pass
    #users: typing.List[User] = strawberry_django.relation_field()
    #tags: typing.List['Tag'] = strawberry_django.relation_field()
    #@strawberry_django.relation_field
    #def users(root, info, qs) -> typing.List[User]:
    #    return qs

@strawberry_django.type(models.Tag, fields=[
    'id',
    'name',
    ('groups', Group),
    ('user', User),
])
class Tag:
    pass

