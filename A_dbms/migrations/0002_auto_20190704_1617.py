# Generated by Django 2.1.3 on 2019-07-04 08:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='stage',
            name='page_amout',
            field=models.IntegerField(default=1, verbose_name='页数'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 7, 4), verbose_name='补调日期'),
        ),
    ]