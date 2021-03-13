from django.conf import settings

TEST_SETTINGS = {
    'DATABASES': {
        "default": { "ENGINE": "django.db.backends.sqlite3" }
    },
    'INSTALLED_APPS': [
        'tests',
    ],
}

settings.configure(**TEST_SETTINGS)
