# Generated by Django 2.1.3 on 2019-07-15 00:17

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0004_auto_20190710_0841'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='stage',
            options={'ordering': ['stage_type', 'id'], 'verbose_name_plural': '追偿-追偿阶段'},
        ),
        migrations.AddField(
            model_name='lendingorder',
            name='lending_state',
            field=models.IntegerField(choices=[(4, '已上会'), (5, '已签批'), (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')], default=4, verbose_name='_次序状态'),
        ),
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 7, 15), verbose_name='补调日期'),
        ),
    ]
