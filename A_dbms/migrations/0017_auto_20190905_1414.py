# Generated by Django 2.1.7 on 2019-09-05 06:14

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0016_auto_20190904_1439'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 9, 5), verbose_name='补调日期'),
        ),
    ]
