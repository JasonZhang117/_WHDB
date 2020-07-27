# Generated by Django 2.1.7 on 2020-02-11 06:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0007_patent'),
    ]

    operations = [
        migrations.AddField(
            model_name='industries',
            name='ind_typ',
            field=models.IntegerField(choices=[(1, '未分产业'), (11, '第一产业'), (21, '第二产业'), (31, '第三产业')], default=1, verbose_name='产业分类'),
        ),
        migrations.AddField(
            model_name='provides',
            name='credit_typ',
            field=models.IntegerField(choices=[(1, '纯信用贷款'), (11, '抵押贷款'), (15, '质押贷款'), (21, '保证贷款'), (99, '其他')], default=99, verbose_name='信用形式分类'),
        ),
        migrations.AddField(
            model_name='provides',
            name='obj_typ',
            field=models.IntegerField(choices=[(1, '农户贷款'), (11, '关联企业或个体工商户贷款'), (15, '个人消费贷款'), (21, '农村企业贷款'), (23, '城市-小微企业'), (25, '城市-小微其他企业'), (99, '其他')], default=99, verbose_name='贷款对象分类'),
        ),
        migrations.AlterField(
            model_name='patent',
            name='patent_ty',
            field=models.IntegerField(verbose_name='分类'),
        ),
        migrations.AlterField(
            model_name='provides',
            name='provide_typ',
            field=models.IntegerField(choices=[(1, '流贷'), (11, '承兑'), (21, '保函'), (31, '委贷'), (41, '过桥贷'), (52, '房抵贷'), (53, '担保贷'), (55, '经营贷'), (57, '消费贷')], verbose_name='放款种类'),
        ),
    ]
