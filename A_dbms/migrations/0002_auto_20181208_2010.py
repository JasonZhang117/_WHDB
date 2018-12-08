# Generated by Django 2.1.3 on 2018-12-08 12:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appraisals',
            name='review_date',
            field=models.DateField(default=datetime.date.today, verbose_name='评审日期'),
        ),
        migrations.AlterField(
            model_name='articles',
            name='sign_type',
            field=models.IntegerField(blank=True, choices=[(1, '同意'), (2, '不同意')], null=True, verbose_name='签批结论'),
        ),
    ]
