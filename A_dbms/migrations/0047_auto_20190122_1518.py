# Generated by Django 2.1.3 on 2019-01-22 07:18

import A_dbms.models.m_agree
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0046_auto_20190121_1814'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='singlequota',
            name='amount',
        ),
        migrations.AddField(
            model_name='singlequota',
            name='single_provide_sum',
            field=models.FloatField(default=0, verbose_name='_放款金额'),
        ),
        migrations.AddField(
            model_name='singlequota',
            name='single_repayment_sum',
            field=models.FloatField(default=0, verbose_name='_还款金额'),
        ),
        migrations.AlterField(
            model_name='agrees',
            name='lending',
            field=models.ForeignKey(limit_choices_to=A_dbms.models.m_agree.limit_agree_choices, on_delete=django.db.models.deletion.PROTECT, related_name='agree_lending', to='A_dbms.LendingOrder', verbose_name='放款纪要'),
        ),
    ]