# Generated by Django 2.1.3 on 2019-01-09 07:36

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0017_auto_20190109_1055'),
    ]

    operations = [
        migrations.AlterField(
            model_name='branches',
            name='cooperator',
            field=models.ForeignKey(limit_choices_to={'cooperator_state': 1}, on_delete=django.db.models.deletion.CASCADE, related_name='branch_cooperator', to='A_dbms.Cooperators', verbose_name='授信银行'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='back_limit',
            field=models.FloatField(default=0, verbose_name='单笔限额（保函）'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='credit_date',
            field=models.DateField(default=datetime.date.today, verbose_name='合作日期'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='flow_credit',
            field=models.FloatField(default=100000000, verbose_name='综合额度'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='flow_limit',
            field=models.FloatField(default=10000000, verbose_name='单笔限额（综合）'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='feedback_buildor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='feedback_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
    ]