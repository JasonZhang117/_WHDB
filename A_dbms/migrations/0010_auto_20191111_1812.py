# Generated by Django 2.1.7 on 2019-11-11 10:12

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0009_auto_20191105_1535'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='investigate',
            options={'ordering': ['-inv_date'], 'verbose_name_plural': '项目-补调'},
        ),
        migrations.AddField(
            model_name='agrees',
            name='acc_bank',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='开户行'),
        ),
        migrations.AddField(
            model_name='agrees',
            name='acc_name',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='开户名'),
        ),
        migrations.AddField(
            model_name='agrees',
            name='acc_num',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='账号'),
        ),
        migrations.AddField(
            model_name='agrees',
            name='due_date',
            field=models.DateField(blank=True, null=True, verbose_name='到期日'),
        ),
        migrations.AddField(
            model_name='agrees',
            name='purpose',
            field=models.CharField(blank=True, max_length=32, null=True, verbose_name='借款用途'),
        ),
        migrations.AddField(
            model_name='agrees',
            name='start_date',
            field=models.DateField(blank=True, null=True, verbose_name='起始日'),
        ),
        migrations.AlterField(
            model_name='agrees',
            name='agree_rate',
            field=models.CharField(max_length=128, verbose_name='收费（利率）'),
        ),
        migrations.AlterField(
            model_name='articles',
            name='borrower',
            field=models.ManyToManyField(blank=True, null=True, related_name='borrower_custom', to='A_dbms.Customes', verbose_name='共借人'),
        ),
        migrations.AlterField(
            model_name='articles',
            name='expert',
            field=models.ManyToManyField(blank=True, null=True, related_name='article_expert', to='A_dbms.Experts', verbose_name='评审委员'),
        ),
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 11, 11), verbose_name='补调日期'),
        ),
    ]
