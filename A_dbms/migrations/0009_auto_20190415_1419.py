# Generated by Django 2.1.3 on 2019-04-15 06:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0008_auto_20190412_1614'),
    ]

    operations = [
        migrations.AddField(
            model_name='warrants',
            name='meeting_date',
            field=models.DateField(blank=True, null=True, verbose_name='最近上会日'),
        ),
        migrations.AlterField(
            model_name='houses',
            name='house_name',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='备注'),
        ),
    ]