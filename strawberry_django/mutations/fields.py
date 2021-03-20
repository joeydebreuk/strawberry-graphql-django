import strawberry
from . import resolvers
from .. import utils


def mutations(*types):
    mutation_fields = {}
    for output_type, input_type in types:
        model = input_type._django_model
        object_name = utils.camel_to_snake(model._meta.object_name)
        mutation_fields[f'create_{object_name}'] = resolvers.create(model, output_type, input_type)
        mutation_fields[f'create_{object_name}s'] = resolvers.create_batch(model, output_type, input_type)
        mutation_fields[f'update_{object_name}s'] = resolvers.update(model, output_type, input_type)
        mutation_fields[f'delete_{object_name}s'] = resolvers.delete(model, output_type, input_type)
    return strawberry.type(type('Mutation', (), mutation_fields))

mutations.create = resolvers.create
mutations.create_batch = resolvers.create_batch
mutations.update = resolvers.update
mutations.delete = resolvers.delete 
