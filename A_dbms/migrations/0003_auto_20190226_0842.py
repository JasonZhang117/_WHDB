# Generated by Django 2.1.3 on 2019-02-26 00:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0002_auto_20190225_2021'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='inquiry',
            name='inquiry_date',
        ),
        migrations.AddField(
            model_name='inquiry',
            name='auction_amount',
            field=models.FloatField(blank=True, null=True, verbose_name='成交金额'),
        ),
        migrations.AddField(
            model_name='inquiry',
            name='auction_date',
            field=models.DateField(blank=True, null=True, verbose_name='拍卖日期'),
        ),
        migrations.AddField(
            model_name='inquiry',
            name='auction_state',
            field=models.IntegerField(choices=[(1, '正常'), (5, '挂网'), (11, '成交'), (21, '流拍'), (31, '回转'), (99, '注销')], default=1, verbose_name='_拍卖状态'),
        ),
        migrations.AddField(
            model_name='inquiry',
            name='listing_price',
            field=models.FloatField(blank=True, null=True, verbose_name='挂网价格'),
        ),
        migrations.AddField(
            model_name='warrants',
            name='listing_price',
            field=models.FloatField(blank=True, null=True, verbose_name='挂网价格'),
        ),
    ]