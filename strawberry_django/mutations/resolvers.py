from typing import List, Optional
import strawberry
from .. import fields, utils
from ..type import generate_update_from_input

def create(model, output_type, input_type):
    @fields.mutation
    def mutation(data: input_type) -> output_type:
        obj_data = utils.get_input_data(model, data)
        obj = model.objects.create(**obj_data)
        update_m2m_fields(model, [obj], data)
        return obj
    return mutation

def create_batch(model, output_type, input_type):
    @fields.mutation
    def mutation(data: List[input_type]) -> List[output_type]:
        objects = []
        for d in data:
            obj_data = utils.get_input_data(model, d)
            obj = model.objects.create(**obj_data)
            objects.append(obj)
            update_m2m_fields(model, [obj], d)
        return objects
    return mutation

def update(model, output_type, input_type):
    update_type = generate_update_from_input(model, input_type)
    @fields.mutation
    def mutation(data: update_type, filters: Optional[List[str]] = []) -> List[output_type]:
        qs = model.objects.all()
        if filters:
            filter, exclude = utils.process_filters(filters)
            qs = qs.filter(**filter).exclude(**exclude)
        update_data = utils.get_input_data(model, data)
        qs.update(**update_data)
        update_m2m_fields(model, qs, data)
        return qs.all()
    return mutation

def delete(model, output_type, input_type):
    @fields.mutation
    def mutation(filters: Optional[List[str]] = []) -> List[strawberry.ID]:
        qs = model.objects.all()
        if filters:
            filter, exclude = utils.process_filters(filters)
            qs = qs.filter(**filter).exclude(**exclude)
        ids = list(qs.values_list('id', flat=True))
        qs.delete()
        return ids
    return mutation

def update_m2m_fields(model, objects, data):
    data = utils.get_input_data_m2m(model, data)
    if not data:
        return
    # iterate through objects and update m2m fields
    for obj in objects:
        for key, actions in data.items():
            relation_field = getattr(obj, key)
            for key, values in actions.items():
                # action is add, set or remove function of relation field
                action = getattr(relation_field, key)
                action(*values)
