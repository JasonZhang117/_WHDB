# Generated by Django 2.1.3 on 2019-04-11 08:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0004_auto_20190409_1847'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='ownership',
            unique_together=set(),
        ),
    ]