# Generated by Django 4.2 on 2023-04-29 16:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homeapp', '0004_routes_date_userbudget_mpg_alter_fuelprice_date_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='routes',
            name='date',
            field=models.DateField(default=None),
        ),
    ]
