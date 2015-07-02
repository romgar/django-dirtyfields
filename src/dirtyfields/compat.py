
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
    try:
        instance.save(update_fields=fields_list.keys())
    except TypeError:
        # django < 1.5 does not support update_fields option on save method
        # TODO: find a workaround for version 1.4.x, for now just saving on the classic way.
        instance.save()
