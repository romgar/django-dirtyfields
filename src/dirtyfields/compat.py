import django
from django.db.models import signals


def is_db_expression(value):
    try:
        # django < 1.8
        from django.db.models.expressions import ExpressionNode
        return isinstance(value, ExpressionNode)
    except ImportError:
        # django >= 1.8  (big refactoring in Lookup/Expressions/Transforms)
        from django.db.models.expressions import BaseExpression, Combinable
        return isinstance(value, (BaseExpression, Combinable))


def save_specific_fields(instance, fields_list):

    if django.VERSION >= (1, 5):
        instance.save(update_fields=fields_list.keys())
    else:
        # dirtyfields is by default returning dirty fields with their old value
        # We should pass the new value(s) to update the database
        new_fields_list = {field_name: getattr(instance, field_name)
                           for field_name, field_value in fields_list.items()}

        # django < 1.5 does not support update_fields option on save method
        instance.__class__.objects.filter(pk=instance.pk).update(**new_fields_list)

        # dirtyfield is based on post_save signal to save last database value in memory.
        # As update() method does not trigger this signal, we launch it explicitly.
        signals.post_save.send(sender=instance.__class__, instance=instance)
