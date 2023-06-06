from django.core.validators import RegexValidator

from rest_framework.serializers import ModelSerializer
from rest_framework.serializers import Serializer, ValidationError
from rest_framework.serializers import CharField, ListField, IntegerField

from .models import Product, Order, OrderContent


class OrderContentSerializer(ModelSerializer):
    product = IntegerField(source="OrderContent.item")
    quantity = IntegerField(
        source="OrderContent.quantity",
        min_value=1,
    )

    class Meta():
        model = OrderContent
        fields = ('id', 'product', 'quantity')

    def validate_product(self, product_id):
        data = Product.objects.filter(id=product_id).first()
        if not data:
            raise ValidationError("Продукт не существует.")
        return data.pk


class OrderSerializer(ModelSerializer):
    firstname = CharField(source="Order.name")
    lastname = CharField(source="Order.surname")
    address = CharField(source="Order.address")
    phonenumber = CharField(
        source="Order.phone",
        max_length=17,
        validators=[
            RegexValidator(
                regex=r'^((\+?7|8)[ \-.]?)?((\([1-9][0-9]{2}\))|([1-9][0-9]{2}))?([ \-.])?(\d{3}[\- .]?\d{2}[\- .]?\d{2})$',
                message="Phone number must be entered in the format '+71234567890'. Up to 13 digits allowed."
            ),
        ],
    )
    products = ListField(
        child=OrderContentSerializer(),
        min_length=1,
        allow_empty=False
    )

    class Meta:
        model = Order
        fields = ('id', 'firstname', 'lastname', 'address', 'phonenumber', 'products')

    def to_representation(self, instance):
        ret = super(OrderSerializer, self).to_representation(instance)
        # check the request is list view or detail view
        print(self)
        is_list_view = isinstance(self.instance, list)
        extra_ret = {'key': 'list value'} if is_list_view else {'key': 'single value'}
        ret.update(extra_ret)
        return ret
