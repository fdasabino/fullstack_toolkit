# Generated by Django 3.1.4 on 2021-12-14 10:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('checkout', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='deliveryoptions',
            name='order',
            field=models.PositiveIntegerField(default=0, help_text='Required', verbose_name='list order'),
        ),
    ]