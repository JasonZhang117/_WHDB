# Generated by Django 2.1.3 on 2019-02-02 03:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0002_auto_20190202_1122'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notify',
            name='time_limit',
            field=models.IntegerField(verbose_name='期限（月）'),
        ),
    ]
