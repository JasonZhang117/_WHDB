# Generated by Django 2.1.3 on 2019-01-06 03:30

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0008_auto_20190106_1123'),
    ]

    operations = [
        migrations.AddField(
            model_name='chattel',
            name='chattel_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='chattel_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='chattel',
            name='chattel_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='draft',
            name='draft_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='draft_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='draft',
            name='draft_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='draftextend',
            name='draft_e_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='draft_e_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='draftextend',
            name='draft_e_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='grounds',
            name='ground_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='ground_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='grounds',
            name='ground_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='houses',
            name='house_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='house_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='houses',
            name='house_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='hypothecs',
            name='hypothec_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='hypothec_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='hypothecs',
            name='hypothec_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='ownership',
            name='ownership_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='ownership_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='ownership',
            name='ownership_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='receivable',
            name='receivable_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='receivable_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='receivable',
            name='receivable_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='receiveextend',
            name='receiv_e_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='receiv_e_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='receiveextend',
            name='receiv_e_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='stockes',
            name='stock_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='stock_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='stockes',
            name='stock_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='vehicle_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='vehicle_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建者'),
        ),
        migrations.AddField(
            model_name='vehicle',
            name='vehicle_date',
            field=models.DateField(default=datetime.date.today, verbose_name='创建日期'),
        ),
    ]
