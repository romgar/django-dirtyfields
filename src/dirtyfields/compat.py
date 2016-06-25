import sys
import django
from django.db.models import signals
from django.db.models.query_utils import DeferredAttribute


def get_m2m_with_model(given_model):
    if django.VERSION < (1, 9):
        return given_model._meta.get_m2m_with_model()
    else:
        return [
            (f, f.model if f.model != given_model else None)
            for f in given_model._meta.get_fields()
            if f.many_to_many and not f.auto_created
        ]


def is_db_expression(value):
    try:
        # django < 1.8
        from django.db.models.expressions import ExpressionNode
        return isinstance(value, ExpressionNode)
    except ImportError:
        # django >= 1.8  (big refactoring in Lookup/Expressions/Transforms)
        from django.db.models.expressions import BaseExpression, Combinable
        return isinstance(value, (BaseExpression, Combinable))


def is_deferred(model, field):
    attr = model.__class__.__dict__.get(field.attname)
    return isinstance(attr, DeferredAttribute)


def save_specific_fields(instance, fields_list):

    if django.VERSION >= (1, 5):
        instance.save(update_fields=fields_list.keys())
    else:
        # dirtyfields is by default returning dirty fields with their old value
        # We should pass the new value(s) to update the database
        new_fields_list = {field_name: getattr(instance, field_name)
                           for field_name, field_value in fields_list.items()}

        # dirtyfield is based on post_save signal to save last database value in memory.
        # As we need to manually launch post_save signal, we also launch pre_save
        # to be coherent with django 'classic' save signals.
        signals.pre_save.send(sender=instance.__class__, instance=instance)

        # django < 1.5 does not support update_fields option on save method
        instance.__class__.objects.filter(pk=instance.pk).update(**new_fields_list)

        # dirtyfield is based on post_save signal to save last database value in memory.
        # As update() method does not trigger this signal, we launch it explicitly.
        signals.post_save.send(sender=instance.__class__, instance=instance)


def is_buffer(value):
    if sys.version_info < (3, 0, 0):
        return isinstance(value, buffer)
    else:
        return isinstance(value, memoryview)
