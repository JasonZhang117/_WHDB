# Generated by Django 2.1.3 on 2019-01-21 10:14

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0045_articles_build_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='ArticleChange',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('change_view', models.IntegerField(choices=[(1, '变更申请'), (11, '同意变更'), (21, '否决变更')], default=1, verbose_name='变更意见')),
                ('change_detail', models.TextField(verbose_name='签批详情')),
                ('change_date', models.DateField(verbose_name='变更日期')),
                ('build_date', models.DateField(default=datetime.date.today, verbose_name='创建日期')),
                ('article', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_article', to='A_dbms.Articles', verbose_name='项目')),
                ('change_buildor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='change_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
            ],
            options={
                'verbose_name_plural': '项目-变更',
                'db_table': 'dbms_articlechange',
            },
        ),
        migrations.AlterField(
            model_name='counters',
            name='counter_typ',
            field=models.IntegerField(choices=[(1, '企业担保'), (2, '个人保证'), (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'), (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (51, '股权预售'), (52, '房产预售'), (53, '土地预售')], verbose_name='合同类型'),
        ),
        migrations.AlterField(
            model_name='feedback',
            name='propose',
            field=models.IntegerField(choices=[(1, '符合上会条件'), (11, '暂不符合上会条件'), (21, '建议终止项目')], verbose_name='上会建议'),
        ),
        migrations.AlterField(
            model_name='lendingsures',
            name='sure_typ',
            field=models.IntegerField(choices=[(1, '企业保证'), (2, '个人保证'), (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'), (21, '房产顺位'), (22, '土地顺位'), (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'), (51, '股权预售'), (52, '房产预售'), (53, '土地预售')], verbose_name='担保类型'),
        ),
    ]