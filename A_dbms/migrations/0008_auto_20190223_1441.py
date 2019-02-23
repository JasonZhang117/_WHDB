# Generated by Django 2.1.3 on 2019-02-23 06:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0007_auto_20190223_1430'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='seal',
            name='sequest_date',
        ),
        migrations.AddField(
            model_name='seal',
            name='inquiry_date',
            field=models.DateField(blank=True, null=True, verbose_name='最近查询日'),
        ),
        migrations.AlterField(
            model_name='seal',
            name='seal_date',
            field=models.DateField(blank=True, null=True, verbose_name='最近查封日'),
        ),
    ]
