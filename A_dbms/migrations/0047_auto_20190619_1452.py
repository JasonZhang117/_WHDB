# Generated by Django 2.1.3 on 2019-06-19 06:52

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0046_auto_20190613_1520'),
    ]

    operations = [
        migrations.AddField(
            model_name='customes',
            name='amount',
            field=models.FloatField(default=0, verbose_name='_余额总额'),
        ),
        migrations.AlterField(
            model_name='customesp',
            name='marital_status',
            field=models.IntegerField(choices=[(1, '未婚'), (11, '已婚'), (21, '离异'), (41, '丧偶'), (99, '------')], default=1, verbose_name='婚姻状况'),
        ),
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 6, 19), verbose_name='补调日期'),
        ),
    ]
