# Generated by Django 2.1.7 on 2019-12-20 03:08

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='resultstate',
            options={'ordering': ['result_typ'], 'verbose_name_plural': '合同-决议及声明'},
        ),
        migrations.AlterField(
            model_name='articles',
            name='article_state',
            field=models.IntegerField(choices=[(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'), (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')], default=1, verbose_name='项目状态'),
        ),
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 12, 20), verbose_name='补调日期'),
        ),
        migrations.AlterField(
            model_name='resultstate',
            name='agree',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='result_agree', to='A_dbms.Agrees', verbose_name='主合同'),
        ),
        migrations.AlterField(
            model_name='resultstate',
            name='result_typ',
            field=models.IntegerField(choices=[(11, '股东会决议'), (13, '合伙人会议决议'), (15, '举办者会议决议'), (21, '董事会决议'), (23, '管委会决议'), (31, '财产声明书'), (41, '个人婚姻状况及财产申明'), (51, '承诺函')], verbose_name='决议类型'),
        ),
        migrations.AlterField(
            model_name='vehicle',
            name='vehicle_brand',
            field=models.CharField(max_length=64, verbose_name='车辆类型'),
        ),
    ]
