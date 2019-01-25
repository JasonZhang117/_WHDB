# Generated by Django 2.1.3 on 2019-01-17 00:40

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0032_auto_20190116_1250'),
    ]

    operations = [
        migrations.AlterField(
            model_name='appraisals',
            name='article',
            field=models.ManyToManyField(blank=True, limit_choices_to={'article_state': 2}, null=True, related_name='appraisal_article', to='A_dbms.Articles', verbose_name='参评项目'),
        ),
        migrations.AlterField(
            model_name='articles',
            name='article_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='article_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='_创建者'),
        ),
        migrations.AlterField(
            model_name='articles',
            name='article_state',
            field=models.IntegerField(choices=[(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'), (6, '已注销')], default=1, verbose_name='_项目状态'),
        ),
    ]