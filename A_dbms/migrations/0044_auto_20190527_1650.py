# Generated by Django 2.1.3 on 2019-05-27 08:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0043_auto_20190527_1649'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appraisals',
            name='compere',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='compere_employee', to=settings.AUTH_USER_MODEL, verbose_name='主持人'),
        ),
    ]
