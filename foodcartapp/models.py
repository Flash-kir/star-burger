import datetime

from django.utils import timezone

from django.db import models
from django.core.validators import MinValueValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.db.models import Sum


class Restaurant(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    address = models.CharField(
        'адрес',
        max_length=100,
        blank=True,
    )
    contact_phone = models.CharField(
        'контактный телефон',
        max_length=50,
        blank=True,
    )

    class Meta:
        verbose_name = 'ресторан'
        verbose_name_plural = 'рестораны'

    def __str__(self):
        return self.name


class ProductQuerySet(models.QuerySet):
    def available(self):
        products = (
            RestaurantMenuItem.objects
            .filter(availability=True)
            .values_list('product')
        )
        return self.filter(pk__in=products)


class ProductCategory(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'категории'

    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(
        'название',
        max_length=50
    )
    category = models.ForeignKey(
        ProductCategory,
        verbose_name='категория',
        related_name='products',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)]
    )
    image = models.ImageField(
        'картинка'
    )
    special_status = models.BooleanField(
        'спец.предложение',
        default=False,
        db_index=True,
    )
    description = models.TextField(
        'описание',
        max_length=200,
        blank=True,
    )

    objects = ProductQuerySet.as_manager()

    class Meta:
        verbose_name = 'товар'
        verbose_name_plural = 'товары'

    def __str__(self):
        return self.name


class RestaurantMenuItem(models.Model):
    restaurant = models.ForeignKey(
        Restaurant,
        related_name='menu_items',
        verbose_name="ресторан",
        on_delete=models.CASCADE,
    )
    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='menu_items',
        verbose_name='продукт',
    )
    availability = models.BooleanField(
        'в продаже',
        default=True,
        db_index=True
    )

    class Meta:
        verbose_name = 'пункт меню ресторана'
        verbose_name_plural = 'пункты меню ресторана'
        unique_together = [
            ['restaurant', 'product']
        ]

    def __str__(self):
        return f"{self.restaurant.name} - {self.product.name}"


class Order(models.Model):
    NEW = 'N'
    COOK = 'C'
    DELIVERY = 'D'
    READY = 'R'
    ORDER_STATUS = (
        ('N', 'Необработанный'),
        ('C', 'Готовится'),
        ('D', 'Передан в доставку'),
        ('R', 'Выполнен'),
    )
    CASH = 'C'
    ELECTRONIC = 'E'
    PAYMENT_METHODS = (
        ('C', 'Наличные'),
        ('E', 'Электронно'),
    )
    name = models.CharField(
        verbose_name='имя',
        max_length=50
    )
    surname = models.CharField(
        verbose_name='отчество',
        max_length=50
    )
    phone = PhoneNumberField(
        region="RU",
        db_index=True,
        verbose_name='телефон'
    )
    address = models.CharField(
        verbose_name='адрес',
        max_length=200
    )
    status = models.CharField(
        max_length=2,
        choices=ORDER_STATUS,
        default=NEW,
        db_index=True,
    )
    payment_method = models.CharField(
        max_length=2,
        choices=PAYMENT_METHODS,
        default=CASH,
        db_index=True,
    )
    comment = models.TextField(
        max_length=300,
        blank=True,
        default=''
    )
    registrated_at = models.DateTimeField(
        default=timezone.now,
        blank=True,
        db_index=True,
    )
    called_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
    )
    delivered_at = models.DateTimeField(
        blank=True,
        null=True,
        db_index=True,
    )

    def get_payment_method_display(self):
        for method in self.PAYMENT_METHODS:
            if self.payment_method == method[0]:
                return method[1]
        return ''

    def get_order_status_display(self):
        for status in self.ORDER_STATUS:
            if self.status == status[0]:
                return status[1]
        return ''

    def __str__(self):
        return f'{self.pk}. {self.surname} {self.name} - {self.phone}({self.address})'


class OrderContent(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        verbose_name='заказ',
        related_name='items'
    )
    item = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,
        verbose_name='продукт',
        related_name='products',
        null=True
    )
    quantity = models.IntegerField(
        verbose_name='количество'
    )
    price = models.DecimalField(
        'цена',
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(0)],
        default=0,
    )

    def calculate_price(self):
        self.price = self.item.price
        self.save()
        return self.price
