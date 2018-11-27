# Generated by Django 2.1.3 on 2018-11-23 09:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0012_auto_20181123_1414'),
    ]

    operations = [
        migrations.CreateModel(
            name='SummaryNum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.CharField(max_length=32, unique=True, verbose_name='单项额度')),
                ('credit_model', models.IntegerField(choices=[(1, '流贷'), (2, '承兑'), (3, '保函')], default=1, verbose_name='授信类型')),
                ('credit_amount', models.FloatField(verbose_name='授信额度（元）')),
                ('flow_rate', models.FloatField(verbose_name='费率（%）')),
            ],
            options={
                'db_table': 'dbms_summarynum',
                'verbose_name_plural': '评审-纪要',
            },
        ),
        migrations.RemoveField(
            model_name='articles',
            name='accept_credit',
        ),
        migrations.RemoveField(
            model_name='articles',
            name='accept_rate',
        ),
        migrations.RemoveField(
            model_name='articles',
            name='flow_credit',
        ),
        migrations.RemoveField(
            model_name='articles',
            name='flow_rate',
        ),
        migrations.RemoveField(
            model_name='articles',
            name='honour_credit',
        ),
        migrations.RemoveField(
            model_name='articles',
            name='honour_rate',
        ),
        migrations.AddField(
            model_name='summaries',
            name='expert',
            field=models.ManyToManyField(related_name='summary_expert', to='A_dbms.Experts', verbose_name='评审'),
        ),
        migrations.AlterField(
            model_name='summaries',
            name='num',
            field=models.CharField(max_length=32, unique=True, verbose_name='_纪要编号'),
        ),
    ]