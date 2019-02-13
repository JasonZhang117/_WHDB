# Generated by Django 2.1.3 on 2019-02-12 01:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0009_auto_20190212_0952'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='compensatories',
            name='retrieve_amount',
        ),
        migrations.AddField(
            model_name='compensatories',
            name='compensatory_amount',
            field=models.FloatField(default=1, verbose_name='代偿总额'),
            preserve_default=False,
        ),
    ]