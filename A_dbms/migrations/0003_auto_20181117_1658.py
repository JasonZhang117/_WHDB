# Generated by Django 2.1.3 on 2018-11-17 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0002_auto_20181116_1448'),
    ]

    operations = [
        migrations.RenameField(
            model_name='jobs',
            old_name='menus',
            new_name='menu',
        ),
    ]