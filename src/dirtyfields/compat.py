
def is_db_expression(value):
    try:
        # django < 1.8
        from django.db.models.expressions import ExpressionNode
        return isinstance(value, ExpressionNode)
    except ImportError:
        # django >= 1.8  (big refactoring in Lookup/Expressions/Transforms)
        from django.db.models.expressions import BaseExpression, Combinable
        return isinstance(value, (BaseExpression, Combinable))
