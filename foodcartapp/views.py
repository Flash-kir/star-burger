from django.http import JsonResponse
from django.templatetags.static import static
from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response

from .models import Product
from .models import Order
from .models import OrderContent


def banners_list_api(request):
    # FIXME move data to db?
    return JsonResponse([
        {
            'title': 'Burger',
            'src': static('burger.jpg'),
            'text': 'Tasty Burger at your door step',
        },
        {
            'title': 'Spices',
            'src': static('food.jpg'),
            'text': 'All Cuisines',
        },
        {
            'title': 'New York',
            'src': static('tasty.jpg'),
            'text': 'Food is incomplete without a tasty dessert',
        }
    ], safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


def product_list_api(request):
    products = Product.objects.select_related('category').available()

    dumped_products = []
    for product in products:
        dumped_product = {
            'id': product.id,
            'name': product.name,
            'price': product.price,
            'special_status': product.special_status,
            'description': product.description,
            'category': {
                'id': product.category.id,
                'name': product.category.name,
            } if product.category else None,
            'image': product.image.url,
            'restaurant': {
                'id': product.id,
                'name': product.name,
            }
        }
        dumped_products.append(dumped_product)
    return JsonResponse(dumped_products, safe=False, json_dumps_params={
        'ensure_ascii': False,
        'indent': 4,
    })


@api_view(['POST'])
def register_order(request):
    print(request.data)
    order_query_content = request.data

    content = {}

    if 'products' not in order_query_content.keys():
        content = {'error': 'products: Обязательное поле.'}
    elif order_query_content['products'] is None:
        content = {'error': 'products: Это поле не может быть пустым.'}
    elif not isinstance(order_query_content['products'], list):
        content = {'error': 'products: Ожидался list со значениями, но был получен "str".'}
    elif len(order_query_content['products']) == 0:
        content = {'error': 'products: Этот список не может быть пустым.'}

    if content:
        return Response(content, status=status.HTTP_200_OK)

    order = Order(
        name=order_query_content['firstname'],
        surname=order_query_content['lastname'],
        address=order_query_content['address'],
        phone=order_query_content['phonenumber']
    )
    order.save()
    for item in order_query_content['products']:
        ordercontent = OrderContent(
            order=order,
            item=Product.objects.get(pk=item['product']),
            quantity=item['quantity']
        )
        ordercontent.save()
    return JsonResponse({})
