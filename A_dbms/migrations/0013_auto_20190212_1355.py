# Generated by Django 2.1.3 on 2019-02-12 05:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0012_auto_20190212_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='customes',
            name='classification',
            field=models.IntegerField(choices=[(1, '正常'), (11, '关注'), (21, '次级'), (31, '可疑'), (41, '损失')], default=1, verbose_name='_风险分类'),
        ),
    ]
