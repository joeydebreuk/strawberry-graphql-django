import pytest

@pytest.fixture
def query(schema):
    def query(query):
        return schema.execute_sync(query)
    return query


def test_query(query, user, group, tag):
    result = query('{ users { id name group { id name tags { id name } } } }')
    assert not result.errors
    assert result.data['users'] == [{
        'id': str(user.id),
        'name': 'user',
        'group': {
            'id': str(group.id),
            'name': 'group',
            'tags': [{
                'id': str(tag.id),
                'name': 'tag',
            }]
        }
    }]


def test_filters(query, user):
    result = query('{ groups { users(filters: ["name__startswith=\'us\'", "name__contains!=\'gr\'"]) { name } } }')
    assert not result.errors
    assert result.data['groups'] == [{ 'users': [{ 'name': 'user' }] }]

    result = query('{ groups { users(filters: ["name!=\'user\'"]) { name } } }')
    assert not result.errors
    assert result.data['groups'] == [{ 'users': [] }]


def test_foreign_key_relation(query, user, group):
    result = query('{ users { name group { name } } }')
    assert not result.errors
    assert result.data['users'] == [{
        'name': 'user',
        'group': {
            'name': 'group',
        },
    }]


def test_foreign_key_relation_reversed(query, user, group):
    result = query('{ groups { name users { name } } }')
    assert not result.errors
    assert result.data['groups'] == [{
        'name': 'group',
        'users': [{
            'name': 'user',
        }],
    }]


def test_one_to_one_relation(query, user, tag):
    result = query('{ users { name tag { name } } }')
    assert not result.errors
    assert result.data['users'] == [{
        'name': 'user',
        'tag': {
            'name': 'tag',
        },
    }]


def test_one_to_one_relation_reversed(query, user, tag):
    result = query('{ tags { name user { name } } }')
    assert not result.errors
    assert result.data['tags'] == [{
        'name': 'tag',
        'user': {
            'name': 'user',
        },
    }]


def test_many_to_many_relation(query, group, tag):
    result = query('{ groups { name tags { name } } }')
    assert not result.errors
    assert result.data['groups'] == [{
        'name': 'group',
        'tags': [{
            'name': 'tag',
        }],
    }]


def test_many_to_many_relation_reversed(query, group):
    result = query('{ tags { name groups { name } } }')
    assert not result.errors
    assert result.data['tags'] == [{
        'name': 'tag',
        'groups': [{
            'name': 'group',
        }],
    }]
