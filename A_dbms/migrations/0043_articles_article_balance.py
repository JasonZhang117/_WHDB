# Generated by Django 2.1.3 on 2019-03-11 05:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0042_lendingorder_lending_balance'),
    ]

    operations = [
        migrations.AddField(
            model_name='articles',
            name='article_balance',
            field=models.FloatField(default=0, verbose_name='_在保余额'),
        ),
    ]
