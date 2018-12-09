# Generated by Django 2.1.3 on 2018-12-08 13:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0002_auto_20181208_2010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customes',
            name='back_credit',
        ),
        migrations.RemoveField(
            model_name='customes',
            name='flow_credit',
        ),
        migrations.AddField(
            model_name='customes',
            name='credit_amount',
            field=models.FloatField(default=0, verbose_name='授信总额（元）'),
        ),
        migrations.AlterField(
            model_name='agrees',
            name='agree_typ',
            field=models.IntegerField(choices=[(1, '单笔'), (2, '最高额'), (3, '保函')], default=1, verbose_name='合同种类'),
        ),
        migrations.AlterField(
            model_name='customes',
            name='accept_loan',
            field=models.FloatField(default=0, verbose_name='承兑余额（元）'),
        ),
        migrations.AlterField(
            model_name='customes',
            name='back_loan',
            field=models.FloatField(default=0, verbose_name='保函余额（元）'),
        ),
        migrations.AlterField(
            model_name='customes',
            name='flow_loan',
            field=models.FloatField(default=0, verbose_name='流贷余额（元）'),
        ),
    ]