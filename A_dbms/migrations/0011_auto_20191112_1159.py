# Generated by Django 2.1.7 on 2019-11-12 03:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0010_auto_20191111_1812'),
    ]

    operations = [
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 11, 12), verbose_name='补调日期'),
        ),
    ]