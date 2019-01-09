# Generated by Django 2.1.3 on 2019-01-09 02:54

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0015_auto_20190108_0922'),
    ]

    operations = [
        migrations.AddField(
            model_name='cooperators',
            name='cooperator_state',
            field=models.IntegerField(choices=[(1, '金融机构'), (2, '律师事务所'), (3, '评估事务所')], default=1, verbose_name='机构类型'),
        ),
        migrations.AddField(
            model_name='cooperators',
            name='due_date',
            field=models.DateField(default=datetime.date.today, verbose_name='到期日'),
        ),
        migrations.AddField(
            model_name='notify',
            name='contract_guaranty',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='保证合同编号'),
        ),
        migrations.AddField(
            model_name='notify',
            name='contracts_lease',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='借款合同编号'),
        ),
        migrations.AddField(
            model_name='notify',
            name='remark',
            field=models.CharField(blank=True, max_length=256, null=True, verbose_name='备注'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='back_loan',
            field=models.FloatField(default=0, verbose_name='_保函放款额度'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='back_used',
            field=models.FloatField(default=0, verbose_name='_保函占用额度'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='flow_loan',
            field=models.FloatField(default=0, verbose_name='_流贷&承兑放款额度'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='flow_used',
            field=models.FloatField(default=0, verbose_name='_流贷&承兑占用额度'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='name',
            field=models.CharField(max_length=32, unique=True, verbose_name='合作机构'),
        ),
        migrations.AlterField(
            model_name='cooperators',
            name='short_name',
            field=models.CharField(max_length=32, unique=True, verbose_name='机构简称'),
        ),
        migrations.AlterField(
            model_name='shareholders',
            name='shareholder_name',
            field=models.CharField(max_length=32, verbose_name='简称'),
        ),
        migrations.AlterUniqueTogether(
            name='shareholders',
            unique_together={('custom', 'shareholder_name')},
        ),
    ]
