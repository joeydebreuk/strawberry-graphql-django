#TODO: add support for input types

class TypeRegister(dict):
    # key can be field name, django model field or django model
    def register(self, key):
        django_model = getattr(key, '_django_model', None)
        if django_model:
            key, type = django_model, key
            self[key] = type
            return type

        def wrapper(type):
            self[key] = type
            return type
        return wrapper
