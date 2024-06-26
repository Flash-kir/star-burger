from django.contrib import admin
from django.shortcuts import reverse, redirect
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils import timezone

from .models import Product
from .models import Restaurant
from .models import RestaurantMenuItem
from .models import Order
from .models import OrderContent
from .models import Address

from restaurateur.geo_utils import calculate_distance


class OrderContentInline(admin.TabularInline):
    model = OrderContent
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    search_fields = [
        'address',
        'name',
        'surname',
        'phonenumber'
    ]
    list_display = [
        'pk',
        'name',
        'surname',
        'address',
        'phonenumber',
    ]
    inlines = [
        OrderContentInline,
    ]

    def response_change(self, request, obj):
        if request.GET.get('next'):
            return redirect(request.GET.get('next'))
        else:
            return super().response_change(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        form = super(OrderAdmin, self).get_form(request, obj, **kwargs)
        form.base_fields['restaurant'].queryset = Restaurant.objects.filter(
            pk__in=obj.restaurants_possibility_make_order()
        )
        return form

    def save_model(self, request, obj, form, change):
        if obj.restaurant and obj.status == obj.NEW:
            obj.status = obj.COOK
            obj.called_at = timezone.now()
        return super().save_model(request, obj, form, change)


@admin.register(OrderContent)
class OrderContentAdmin(admin.ModelAdmin):
    search_fields = [
        'order',
        'item'
    ]
    list_display = [
        'pk',
        'order',
        'item',
        'quantity',
        'price',
    ]


class RestaurantMenuItemInline(admin.TabularInline):
    model = RestaurantMenuItem
    extra = 0


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    search_fields = [
        'address',
        'lat',
        'lon',
    ]
    list_display = [
        'pk',
        'address',
        'lat',
        'lon',
    ]


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    search_fields = [
        'name',
        'address',
        'contact_phone',
    ]
    list_display = [
        'name',
        'address',
        'contact_phone',
    ]
    inlines = [
        RestaurantMenuItemInline
    ]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = [
        'get_image_list_preview',
        'name',
        'category',
        'price',
    ]
    list_display_links = [
        'name',
    ]
    list_filter = [
        'category',
    ]
    search_fields = [
        # FIXME SQLite can not convert letter case for cyrillic words properly,
        # so search will be buggy.
        # Migration to PostgreSQL is necessary
        'name',
        'category__name',
    ]

    inlines = [
        RestaurantMenuItemInline
    ]
    fieldsets = (
        ('Общее', {
            'fields': [
                'name',
                'category',
                'image',
                'get_image_preview',
                'price',
            ]
        }),
        ('Подробно', {
            'fields': [
                'special_status',
                'description',
            ],
            'classes': [
                'wide'
            ],
        }),
    )

    readonly_fields = [
        'get_image_preview',
    ]

    class Media:
        css = {
            "all": (
                static("admin/foodcartapp.css")
            )
        }

    def get_image_preview(self, obj):
        if not obj.image:
            return 'выберите картинку'
        return format_html(
            '<img src="{url}" style="max-height: 200px;"/>',
            url=obj.image.url
        )
    get_image_preview.short_description = 'превью'

    def get_image_list_preview(self, obj):
        if not obj.image or not obj.id:
            return 'нет картинки'
        edit_url = reverse('admin:foodcartapp_product_change', args=(obj.id,))
        return format_html(
            '<a href="{edit_url}"><img src="{src}" style="max-height: 50px;"/></a>',
            edit_url=edit_url,
            src=obj.image.url
        )
    get_image_list_preview.short_description = 'превью'
