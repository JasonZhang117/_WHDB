# Generated by Django 2.1.7 on 2019-11-05 07:35

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0008_auto_20191028_1243'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='standing',
            options={'ordering': ['-standingor_date'], 'verbose_name_plural': '追偿-跟进台账'},
        ),
        migrations.AddField(
            model_name='articles',
            name='borrower',
            field=models.ManyToManyField(related_name='borrower_custom', to='A_dbms.Customes', verbose_name='共借人'),
        ),
        migrations.AlterField(
            model_name='customes',
            name='contact_num',
            field=models.CharField(max_length=32, verbose_name='联系电话'),
        ),
        migrations.AlterField(
            model_name='housebag',
            name='housebag_app',
            field=models.IntegerField(choices=[(1, '住宅'), (5, '住宅、住宅地下室'), (11, '商业'), (12, '商业服务'), (21, '办公'), (31, '公寓'), (41, '生产性工业用房'), (42, '非生产性工业用房'), (43, '厂房'), (44, '工业性科研用房'), (45, '工业'), (46, '非生产性工业科研用房'), (47, '营业房'), (48, '研发中心'), (49, '研发楼'), (51, '科研'), (52, '车间'), (53, '消防通道'), (54, '倒班房'), (55, '倒班房及食堂'), (56, '农贸市场'), (61, '车库'), (62, '车位'), (63, '首层机动车停车场'), (64, '机动车库'), (65, '机动车停车库'), (71, '仓储'), (72, '仓储用房及配送用房'), (73, '物流配送中心用房'), (74, '连廊'), (75, '自行车库'), (76, '生产用房'), (77, '库房'), (81, '在建工程'), (91, '其他'), (99, '期房')], default=1, verbose_name='房产用途'),
        ),
        migrations.AlterField(
            model_name='houses',
            name='house_app',
            field=models.IntegerField(choices=[(1, '住宅'), (5, '住宅、住宅地下室'), (11, '商业'), (12, '商业服务'), (21, '办公'), (31, '公寓'), (41, '生产性工业用房'), (42, '非生产性工业用房'), (43, '厂房'), (44, '工业性科研用房'), (45, '工业'), (46, '非生产性工业科研用房'), (47, '营业房'), (48, '研发中心'), (49, '研发楼'), (51, '科研'), (52, '车间'), (53, '消防通道'), (54, '倒班房'), (55, '倒班房及食堂'), (56, '农贸市场'), (61, '车库'), (62, '车位'), (63, '首层机动车停车场'), (64, '机动车库'), (65, '机动车停车库'), (71, '仓储'), (72, '仓储用房及配送用房'), (73, '物流配送中心用房'), (74, '连廊'), (75, '自行车库'), (76, '生产用房'), (77, '库房'), (81, '在建工程'), (91, '其他'), (99, '期房')], default=1, verbose_name='房产用途'),
        ),
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 11, 5), verbose_name='补调日期'),
        ),
    ]
