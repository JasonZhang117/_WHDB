# Generated by Django 2.1.3 on 2018-11-23 06:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0010_auto_20181123_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='summaries',
            name='article',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='summary_article', to='A_dbms.Articles', verbose_name='审保会'),
        ),
    ]