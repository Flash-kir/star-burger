from django import template

register = template.Library()


@register.filter
def status(order):
    return order.get_order_status_display()
