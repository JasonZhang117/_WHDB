# Generated by Django 2.1.3 on 2018-12-24 13:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0004_articles_review_date'),
    ]

    operations = [
        migrations.CreateModel(
            name='LendingCustoms',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('custome', models.ManyToManyField(related_name='lending_custome', to='A_dbms.Customes', verbose_name='反担保人')),
                ('sure', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='custome_sure', to='A_dbms.LendingSures', verbose_name='反担保措施')),
            ],
            options={
                'db_table': 'dbms_lending_custom',
                'verbose_name_plural': '反担保-保证反担保',
            },
        ),
        migrations.CreateModel(
            name='LendingWarrants',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sure', models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='warrant_sure', to='A_dbms.LendingSures', verbose_name='反担保措施')),
                ('warrant', models.ManyToManyField(related_name='lending_warrant', to='A_dbms.Warrants', verbose_name='抵质押物')),
            ],
            options={
                'db_table': 'dbms_lending_warrant',
                'verbose_name_plural': '反担保-抵质押',
            },
        ),
        migrations.RemoveField(
            model_name='mortgageextends',
            name='sure',
        ),
        migrations.RemoveField(
            model_name='mortgageextends',
            name='warrant',
        ),
        migrations.RemoveField(
            model_name='sureextends',
            name='custome',
        ),
        migrations.RemoveField(
            model_name='sureextends',
            name='sure',
        ),
        migrations.RemoveField(
            model_name='articles',
            name='buildor',
        ),
        migrations.AddField(
            model_name='articles',
            name='article_buildor',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.PROTECT, related_name='article_buildor_employee', to=settings.AUTH_USER_MODEL, verbose_name='创建人'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='appraisals',
            name='meeting_state',
            field=models.IntegerField(choices=[(1, '待上会'), (2, '已上会')], default=1, verbose_name='会议状态'),
        ),
        migrations.DeleteModel(
            name='MortgageExtends',
        ),
        migrations.DeleteModel(
            name='SureExtends',
        ),
    ]
