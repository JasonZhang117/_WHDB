# Generated by Django 2.1.3 on 2019-04-24 01:16

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0014_auto_20190424_0753'),
    ]

    operations = [
        migrations.CreateModel(
            name='ResultState',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('result_typ', models.IntegerField(choices=[(11, '股东会决议'), (21, '董事会决议'), (31, '弃权声明'), (41, '单身声明')], verbose_name='决议类型')),
                ('result_date', models.DateField(default=datetime.date.today, verbose_name='创建日期')),
                ('agree', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='result_agree', to='A_dbms.Agrees', verbose_name='主合同')),
                ('custom', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='result_custom', to='A_dbms.Customes', verbose_name='客户')),
                ('resultor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='resultor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
            ],
            options={
                'db_table': 'dbms_resultstate',
                'verbose_name_plural': '合同-决议及声明',
            },
        ),
        migrations.AlterField(
            model_name='countersassure',
            name='counter_assure_buildor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='counter_assureor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AlterField(
            model_name='counterswarrants',
            name='counter_warrant_buildor',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='counter_warrantor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AlterUniqueTogether(
            name='resultstate',
            unique_together={('agree', 'custom', 'result_typ')},
        ),
    ]