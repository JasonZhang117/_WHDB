# Generated by Django 2.1.3 on 2019-01-06 03:14

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0006_auto_20190105_2018'),
    ]

    operations = [
        migrations.AddField(
            model_name='counters',
            name='counter_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='countersassure',
            name='counter_assure_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='counter_assure_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='countersassure',
            name='counter_assure_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='counterswarrants',
            name='counter_warrant_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='counter_warrant_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='counterswarrants',
            name='counter_warrant_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AlterField(
            model_name='agrees',
            name='agree_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='agree_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
        ),
        migrations.AlterField(
            model_name='agrees',
            name='agree_state',
            field=models.IntegerField(choices=[(11, '待签批'), (21, '已签批'), (31, '已落实'), (41, '已放款'), (51, '待变更'), (61, '已解保'), (99, '已作废')], default=11, verbose_name='_合同状态'),
        ),
        migrations.AlterField(
            model_name='counters',
            name='counter_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='counter_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='counters',
            name='counter_state',
            field=models.IntegerField(choices=[(11, '未签订'), (21, '已签订'), (31, '已注销')], default=1, verbose_name='_签订情况'),
        ),
        migrations.AlterField(
            model_name='warrants',
            name='warrant_state',
            field=models.IntegerField(choices=[(1, '未入库'), (2, '已入库'), (3, '已出库'), (4, '已借出'), (5, '已注销'), (6, '无需入库')], default=1, verbose_name='_权证状态'),
        ),
    ]