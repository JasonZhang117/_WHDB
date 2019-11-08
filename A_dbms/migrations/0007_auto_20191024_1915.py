# Generated by Django 2.1.7 on 2019-10-24 11:15

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0006_auto_20191023_1802'),
    ]

    operations = [
        migrations.AddField(
            model_name='agrees',
            name='other',
            field=models.TextField(blank=True, null=True, verbose_name='其他约定'),
        ),
        migrations.AddField(
            model_name='counters',
            name='other',
            field=models.TextField(blank=True, null=True, verbose_name='其他约定'),
        ),
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 10, 24), verbose_name='补调日期'),
        ),
    ]