from django import template
from django.utils.safestring import mark_safe
from foodcartapp.models import Restaurant
from restaurateur.geo_utils import calculate_distance, distance_text

register = template.Library()


@register.filter
def status(order):
    return order.get_order_status_display()


@register.filter
def payment_method(order):
    return order.get_payment_method_display()


@register.filter(is_safe=True)
def restaurants_list(order):
    html_response = ''
    if order.restaurant:
        distance = calculate_distance(order.address, order.restaurant.address)
        html_response = f'Готовит: <p>{order.restaurant.name}{distance_text(distance)}</p>'
    else:
        restaurants_allow = list(
            Restaurant.objects.filter(
                pk__in=order.restaurants_possibility_make_order()
            )
        )
        if restaurants_allow:
            restaurants_for_sort = []
            for restaurant in restaurants_allow:
                order_dist = restaurant.distances.get_or_create(
                                   order=order, restaurant=restaurant
                )[0]
                if not order_dist.distance:
                    distance = calculate_distance(
                                    order.address,
                                    restaurant.address
                    )
                    restaurants_for_sort.append((distance, restaurant))
                    if distance:
                        order_dist.distance = distance
                        order_dist.save()
                else:
                    restaurants_for_sort.append(
                        (order_dist.distance, restaurant)
                    )

            sorted_restaurants = sorted(
                restaurants_for_sort, key=lambda restaurant: restaurant[0]
            )
            html_response = 'Может быть приготовлен ресторанами: <ul>'
            for distance, restaurant in sorted_restaurants:
                html_response += f'<li>{restaurant.name}{distance_text(distance)}</li>'
            html_response += '</ul>'
        else:
            html_response = '<p style="color: red">Ни один ресторан не может приготовить заказ целиком.</p>'
    return mark_safe(html_response)
