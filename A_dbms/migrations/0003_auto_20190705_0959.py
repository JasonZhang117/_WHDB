# Generated by Django 2.1.3 on 2019-07-05 01:59

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0002_auto_20190704_1617'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stage',
            options={'ordering': ['stage_type', 'stage_file'], 'verbose_name_plural': '追偿-追偿阶段'},
        ),
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 7, 5), verbose_name='补调日期'),
        ),
    ]