# Generated by Django 2.1.3 on 2019-04-28 06:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0023_auto_20190428_1430'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='track',
            options={'ordering': ['plan_date'], 'verbose_name_plural': '项目-跟踪'},
        ),
    ]