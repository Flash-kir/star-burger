from django.http import JsonResponse
from django.templatetags.static import static
from django.db import transaction

from rest_framework.decorators import api_view
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import ValidationError
from rest_framework.renderers import JSONRenderer

from .models import Product
from .models import Order
from .models import OrderContent

from .validators import OrderSerializer
from .validators import OrderContentSerializer


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
    serializer = OrderSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    products = request.data.get('products', [])
    if not isinstance(products, list):
        raise ValidationError('Expects products field be a list')

    for items in products:
        serializer_products = OrderContentSerializer(data=items)
        serializer_products.is_valid(raise_exception=True)

    order_query_content = serializer.validated_data

    with transaction.atomic():
        try:
            order = Order(
                name=order_query_content['Order']['name'],
                surname=order_query_content['Order']['surname'],
                address=order_query_content['Order']['address'],
                phone=order_query_content['Order']['phone']
            )
            order.save()

            for item in order_query_content['products']:
                ordercontent = OrderContent(
                    order=order,
                    item=Product.objects.get(pk=item['OrderContent']['item']),
                    quantity=item['OrderContent']['quantity']
                )
                ordercontent.save()

                ordercontent.calculate_price()
        except Exception:
            if order:
                order.delete()

    return Response(serializer.validated_data)
