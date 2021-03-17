import pytest
import strawberry
import strawberry_django
from .. import models, types

@pytest.fixture
def tag(db):
    tag = models.Tag.objects.create(name='tag')
    return tag

@pytest.fixture
def group(db, tag):
    group = models.Group.objects.create(name='group')
    group.tags.add(tag)
    return group

@pytest.fixture
def user(db, group, tag):
    user = models.User.objects.create(name='user', group=group, tag=tag)
    return user

@pytest.fixture
def schema():
    Query = strawberry_django.queries(types.User, types.Group, types.Tag)
    schema = strawberry.Schema(query=Query)
    #print(schema)
    return schema
