# Generated by Django 2.1.3 on 2019-02-21 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0036_auto_20190221_1822'),
    ]

    operations = [
        migrations.AlterField(
            model_name='charge',
            name='charge_date',
            field=models.DateField(verbose_name='支付日期'),
        ),
    ]
