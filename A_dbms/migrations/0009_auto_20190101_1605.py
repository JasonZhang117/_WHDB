# Generated by Django 2.1.3 on 2019-01-01 08:05

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0008_auto_20190101_1538'),
    ]

    operations = [
        migrations.CreateModel(
            name='Review',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('review_sty', models.IntegerField(choices=[(1, '现场检查'), (2, '电话回访')], default=1, verbose_name='保后方式')),
                ('analysis', models.TextField(verbose_name='风险分析')),
                ('suggestion', models.TextField(verbose_name='建议')),
                ('control_option', models.TextField(verbose_name='风控意见')),
                ('review_date', models.DateField(default=datetime.date.today, verbose_name='提交日期')),
                ('custom', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='review_custom', to='A_dbms.Customes', verbose_name='客户')),
                ('reviewor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='reviewor_employee', to=settings.AUTH_USER_MODEL, verbose_name='保后人员')),
            ],
            options={
                'verbose_name_plural': '项目-保后检查',
                'db_table': 'dbms_review',
            },
        ),
        migrations.AlterModelOptions(
            name='compensatories',
            options={'verbose_name_plural': '追偿-代偿'},
        ),
    ]
