# Generated by Django 2.1 on 2020-07-27 08:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0017_auto_20200727_1617'),
    ]

    operations = [
        migrations.AddField(
            model_name='customes',
            name='book',
            field=models.TextField(blank=True, null=True, verbose_name='专员台账'),
        ),
        migrations.AddField(
            model_name='review',
            name='book',
            field=models.TextField(blank=True, null=True, verbose_name='专员台账'),
        ),
    ]