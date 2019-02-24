# Generated by Django 2.1.3 on 2019-02-23 10:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0012_auto_20190223_1828'),
    ]

    operations = [
        migrations.AddField(
            model_name='warrants',
            name='auction_amount',
            field=models.FloatField(blank=True, null=True, verbose_name='成交金额'),
        ),
        migrations.AddField(
            model_name='warrants',
            name='auction_date',
            field=models.DateField(blank=True, null=True, verbose_name='拍卖日期'),
        ),
        migrations.AddField(
            model_name='warrants',
            name='auction_remark',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='拍卖情况'),
        ),
        migrations.AddField(
            model_name='warrants',
            name='auction_state',
            field=models.IntegerField(choices=[(1, '挂网'), (11, '成交'), (21, '流拍'), (31, '回转'), (99, '注销')], default=1, verbose_name='_权证状态'),
        ),
        migrations.AlterField(
            model_name='inquiry',
            name='seal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='inquiry_seal', to='A_dbms.Seal', verbose_name='财产线索'),
        ),
        migrations.AlterField(
            model_name='sealup',
            name='seal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='sealup_seal', to='A_dbms.Seal', verbose_name='财产线索'),
        ),
    ]
