# Generated by Django 2.1.3 on 2019-03-11 00:28

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0038_auto_20190311_0800'),
    ]

    operations = [
        migrations.RenameField(
            model_name='provides',
            old_name='balance',
            new_name='provide_balance',
        ),
    ]
