# Generated by Django 2.1.3 on 2019-01-26 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0069_auto_20190126_2059'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customes',
            name='short_name',
            field=models.CharField(default='1', max_length=16, unique=True, verbose_name='客户简称'),
            preserve_default=False,
        ),
    ]
