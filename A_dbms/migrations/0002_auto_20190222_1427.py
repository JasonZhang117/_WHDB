# Generated by Django 2.1.3 on 2019-02-22 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dun',
            name='award_num',
        ),
        migrations.RemoveField(
            model_name='dun',
            name='judgment',
        ),
    ]
