# Generated by Django 2.1.3 on 2019-01-24 06:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0059_evaluate_evaluate_explain'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='warrants',
            name='warrant_detail',
        ),
        migrations.AddField(
            model_name='warrants',
            name='evaluate_explain',
            field=models.CharField(blank=True, max_length=128, null=True, verbose_name='评估说明'),
        ),
        migrations.AddField(
            model_name='warrants',
            name='evaluate_state',
            field=models.IntegerField(blank=True, choices=[(1, '机构评估'), (11, '机构预估'), (21, '综合询价'), (31, '购买成本')], null=True, verbose_name='评估方式'),
        ),
    ]
