# Generated by Django 2.1.3 on 2018-11-19 05:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0005_employees_department'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='employees',
            name='department',
        ),
        migrations.AddField(
            model_name='employees',
            name='department',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='employee_department', to='A_dbms.Departments', verbose_name='部门'),
            preserve_default=False,
        ),
    ]
