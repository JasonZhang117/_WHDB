# Generated by Django 2.1.7 on 2019-08-30 03:55

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0013_auto_20190805_0811'),
    ]

    operations = [
        migrations.CreateModel(
            name='LetterGuarantee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('guarantee_typ', models.IntegerField(choices=[(1, '履约保函'), (11, '投标保函'), (21, '预付款保函')], verbose_name='保函类型')),
                ('beneficiary', models.CharField(max_length=32, verbose_name='受益人')),
                ('basic_contract', models.CharField(max_length=64, verbose_name='基础合同名称')),
                ('basic_contract_num', models.CharField(max_length=64, verbose_name='基础合同编号')),
                ('starting_date', models.DateField(blank=True, null=True, verbose_name='起始日期')),
                ('due_date', models.DateField(default=datetime.date.today, verbose_name='到期日')),
                ('guarantee_number', models.CharField(max_length=32, verbose_name='保函编号')),
                ('counter_view', models.TextField(blank=True, null=True, verbose_name='保函预览')),
                ('create_date', models.DateField(default=datetime.date.today, verbose_name='创建日期')),
                ('agree', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='guarantee_agree', to='A_dbms.Agrees', verbose_name='委托保证合同')),
                ('creator', models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='creator_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者')),
            ],
            options={
                'verbose_name_plural': '合同-保函',
                'db_table': 'dbms_letter_guarantee',
            },
        ),
        migrations.AlterModelOptions(
            name='sealup',
            options={'ordering': ['-sealupor_date'], 'verbose_name_plural': '追偿-查封明细'},
        ),
        migrations.AlterModelOptions(
            name='shareholders',
            options={'ordering': ['-shareholding_ratio'], 'verbose_name_plural': '客户-股东信息'},
        ),
        migrations.AlterField(
            model_name='customes',
            name='add_amount',
            field=models.IntegerField(default=0, verbose_name='补调次数'),
        ),
        migrations.AlterField(
            model_name='customes',
            name='review_amount',
            field=models.IntegerField(default=0, verbose_name='保后次数'),
        ),
        migrations.AlterField(
            model_name='evaluate',
            name='evaluate_state',
            field=models.IntegerField(choices=[(0, '待评估'), (1, '机构评估'), (11, '机构预估'), (12, '机构口评'), (21, '综合询价'), (31, '购买成本'), (41, '拍卖评估'), (99, '无需评估')], default=1, verbose_name='评估方式'),
        ),
        migrations.AlterField(
            model_name='housebag',
            name='housebag_app',
            field=models.IntegerField(choices=[(1, '住宅'), (11, '商业'), (21, '办公'), (31, '公寓'), (41, '生产性工业用房'), (42, '非生产性工业用房'), (43, '厂房'), (44, '工业性科研用房'), (45, '工业'), (46, '非生产性工业科研用房'), (47, '营业房'), (48, '研发中心'), (51, '科研'), (52, '车间'), (53, '消防通道'), (54, '倒班房'), (61, '车库'), (62, '车位'), (63, '首层机动车停车场'), (64, '机动车库'), (71, '仓储'), (72, '仓储用房及配送用房'), (73, '物流配送中心用房'), (74, '连廊'), (75, '自行车库'), (76, '生产用房'), (77, '库房'), (81, '在建工程'), (91, '其他'), (99, '期房')], default=1, verbose_name='房产用途'),
        ),
        migrations.AlterField(
            model_name='houses',
            name='house_app',
            field=models.IntegerField(choices=[(1, '住宅'), (11, '商业'), (21, '办公'), (31, '公寓'), (41, '生产性工业用房'), (42, '非生产性工业用房'), (43, '厂房'), (44, '工业性科研用房'), (45, '工业'), (46, '非生产性工业科研用房'), (47, '营业房'), (48, '研发中心'), (51, '科研'), (52, '车间'), (53, '消防通道'), (54, '倒班房'), (61, '车库'), (62, '车位'), (63, '首层机动车停车场'), (64, '机动车库'), (71, '仓储'), (72, '仓储用房及配送用房'), (73, '物流配送中心用房'), (74, '连廊'), (75, '自行车库'), (76, '生产用房'), (77, '库房'), (81, '在建工程'), (91, '其他'), (99, '期房')], default=1, verbose_name='房产用途'),
        ),
        migrations.AlterField(
            model_name='investigate',
            name='inv_date',
            field=models.DateField(default=datetime.date(2019, 8, 30), verbose_name='补调日期'),
        ),
        migrations.AlterField(
            model_name='warrants',
            name='evaluate_state',
            field=models.IntegerField(choices=[(0, '待评估'), (1, '机构评估'), (11, '机构预估'), (12, '机构口评'), (21, '综合询价'), (31, '购买成本'), (41, '拍卖评估'), (99, '无需评估')], default=0, verbose_name='评估方式'),
        ),
    ]
