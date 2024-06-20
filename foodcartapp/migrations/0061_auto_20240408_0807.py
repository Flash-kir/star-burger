# Generated by Django 3.2.15 on 2024-04-08 08:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0060_auto_20240212_0645'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='phone',
            new_name='phonenumber',
        ),
        migrations.AlterField(
            model_name='ordercontent',
            name='item',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='products', to='foodcartapp.product', verbose_name='продукт'),
        ),
        migrations.DeleteModel(
            name='OrderDistance',
        ),
    ]