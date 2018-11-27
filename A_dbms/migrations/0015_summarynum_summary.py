# Generated by Django 2.1.3 on 2018-11-26 05:06

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0014_auto_20181126_1303'),
    ]

    operations = [
        migrations.AddField(
            model_name='summarynum',
            name='summary',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='summarynum_summary', to='A_dbms.Articles', verbose_name='纪要'),
            preserve_default=False,
        ),
    ]