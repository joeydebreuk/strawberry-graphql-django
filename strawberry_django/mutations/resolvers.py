from typing import List, Optional
import strawberry
from .. import fields, utils

def create(input_type, output_type):
    model = input_type._django_model
    @fields.mutation
    def mutation(data: input_type) -> output_type:
        data = utils.get_input_data(model, data)
        return model.objects.create(**data)
    return mutation

def create_batch(input_type, output_type):
    model = input_type._django_model
    @fields.mutation
    def mutation(data: List[input_type]) -> List[output_type]:
        objects = []
        for d in data:
            d = utils.get_input_data(model, d)
            obj = model.objects.create(**d)
            objects.append(obj)
        return objects
    return mutation

def update(input_type, output_type):
    model = input_type._django_model
    @fields.mutation
    def mutation(data: input_type, filters: List[str]) -> List[output_type]:
        qs = model.objects.all()
        if filters:
            filter, exclude = utils.process_filters(filters)
            qs = qs.filter(**filter).exclude(**exclude)
        data = utils.get_input_data(model, data)
        qs.update(**data)
        return qs.all()
    return mutation

def delete(input_type, output_type):
    model = input_type._django_model
    @fields.mutation
    def mutation(filters: List[str]) -> List[strawberry.ID]:
        qs = model.objects.all()
        if filters:
            filter, exclude = utils.process_filters(filters)
            qs = qs.filter(**filter).exclude(**exclude)
        ids = list(qs.values_list('id', flat=True))
        qs.delete()
        return ids
    return mutation
