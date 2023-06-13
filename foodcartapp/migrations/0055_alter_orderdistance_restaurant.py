# Generated by Django 3.2.15 on 2023-06-13 10:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('foodcartapp', '0054_alter_orderdistance_distance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderdistance',
            name='restaurant',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='distances', to='foodcartapp.restaurant', verbose_name='расстояние'),
        ),
    ]
