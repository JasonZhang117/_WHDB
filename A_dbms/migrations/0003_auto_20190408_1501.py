# Generated by Django 2.1.3 on 2019-04-08 07:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0002_auto_20190408_1459'),
    ]

    operations = [
        migrations.AlterField(
            model_name='agrees',
            name='agree_name',
            field=models.IntegerField(choices=[(1, '委托保证合同'), (11, '最高额委托保证合同'), (21, '委托出具分离式保函合同'), (31, '借款合同')], verbose_name='合同种类'),
        ),
    ]