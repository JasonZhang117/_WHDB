# Generated by Django 2.1.3 on 2019-02-21 00:21

import A_dbms.models.m_agree
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0026_draftextend_draft_state'),
    ]

    operations = [
        migrations.CreateModel(
            name='Dun',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=128, unique=True, verbose_name='追偿')),
                ('dun_stage', models.IntegerField(choices=[(1, '起诉'), (2, '判决'), (3, '执行'), (4, '和解结案'), (5, '终止执行')], default=1, verbose_name='追偿状态')),
                ('compensatory', models.ManyToManyField(related_name='dun_compensatory', to='A_dbms.Compensatories', verbose_name='代偿')),
            ],
            options={
                'db_table': 'dbms_dun',
                'verbose_name_plural': '追偿-追偿',
            },
        ),
        migrations.AlterField(
            model_name='agrees',
            name='lending',
            field=models.ForeignKey(limit_choices_to=A_dbms.models.m_agree.limit_agree_choices, on_delete=django.db.models.deletion.PROTECT, related_name='agree_lending', to='A_dbms.LendingOrder', verbose_name='放款纪要'),
        ),
    ]
