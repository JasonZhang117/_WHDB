# Generated by Django 2.1.3 on 2018-11-28 05:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0022_auto_20181127_1305'),
    ]

    operations = [
        migrations.AddField(
            model_name='appraisals',
            name='meeting_state',
            field=models.IntegerField(choices=[(1, '待上会'), (2, '已上会')], default=1, verbose_name='项目状态'),
        ),
        migrations.AlterField(
            model_name='appraisals',
            name='num',
            field=models.CharField(max_length=32, unique=True, verbose_name='评审会编号'),
        ),
        migrations.AlterField(
            model_name='experts',
            name='level',
            field=models.IntegerField(choices=[(1, '一级'), (2, '二级'), (3, '内部')], default=1, verbose_name='级别'),
        ),
    ]
