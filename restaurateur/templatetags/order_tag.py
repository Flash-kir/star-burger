from django import template
from django.utils.safestring import mark_safe
from foodcartapp.models import Restaurant, RestaurantMenuItem

register = template.Library()


@register.filter
def status(order):
    return order.get_order_status_display()


@register.filter
def payment_method(order):
    return order.get_payment_method_display()


def resta_urants_possibility_make_order(self):
    actual_menus = {}
    menu_items = list(RestaurantMenuItem.objects.filter(availability=True).values_list('restaurant', 'product'))
    for item in menu_items:
        if item[0] not in actual_menus.keys():
            actual_menus[item[0]] = []
        actual_menus[item[0]].append(item[1])
    item_list = self.get_order_items_list()
    restaurant_list = []
    for restaurant, products_list in actual_menus.items():
        if set(item_list).issubset(set(products_list)):
            restaurant_list.append(restaurant)
    return restaurant_list


@register.filter(is_safe=True)
def restaurants_list(order):
    html_response = ''
    if order.restaurant:
        html_response = f'Готовит: <p>{order.restaurant.name}</p>'
    else:
        resaurants_list = Restaurant.objects.filter(pk__in=order.restaurants_possibility_make_order())
        if resaurants_list:
            html_response = 'Может быть приготовлен ресторанами: <ul>'
            for restaurant in resaurants_list:
                html_response += f'<li>{restaurant.name}</li>'
            html_response += '</ul>'
        else:
            html_response = 'Ни один ресторан не может приготовить заказ целиком.'
    return mark_safe(html_response)
