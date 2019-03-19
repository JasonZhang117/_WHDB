# Generated by Django 2.1.3 on 2019-03-19 03:03

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0053_auto_20190319_0940'),
    ]

    operations = [
        migrations.CreateModel(
            name='Construction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('coustruct_locate', models.CharField(max_length=64, verbose_name='土地坐落')),
                ('coustruct_app', models.IntegerField(choices=[(91, '在建工程')], default=91, verbose_name='土地用途')),
                ('coustruct_area', models.FloatField(verbose_name='土地面积')),
                ('coustructor_date', models.DateField(default=datetime.date.today, verbose_name='创建日期')),
                ('coustructor', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='coustructor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
            ],
            options={
                'db_table': 'dbms_construction',
                'verbose_name_plural': '权证-在建工程',
            },
        ),
        migrations.AlterField(
            model_name='warrants',
            name='warrant_typ',
            field=models.IntegerField(choices=[(1, '房产'), (2, '房产包'), (5, '土地使用权'), (6, '在建工程'), (11, '应收账款'), (21, '股权'), (31, '票据'), (41, '车辆'), (45, '动产'), (51, '其他'), (99, '他权')], default=1, verbose_name='权证类型'),
        ),
        migrations.AddField(
            model_name='construction',
            name='warrant',
            field=models.OneToOneField(limit_choices_to={'warrant_typ': 6}, on_delete=django.db.models.deletion.PROTECT, related_name='coustruct_warrant', to='A_dbms.Warrants', verbose_name='权证'),
        ),
    ]
