# Generated by Django 2.1.3 on 2018-11-23 05:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0008_auto_20181121_1719'),
    ]

    operations = [
        migrations.CreateModel(
            name='Summaries',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('num', models.CharField(blank=True, max_length=32, null=True, unique=True, verbose_name='_纪要编号')),
            ],
        ),
        migrations.AlterField(
            model_name='appraisals',
            name='expert',
            field=models.ManyToManyField(related_name='appraisal_expert', to='A_dbms.Experts', verbose_name='评审委员'),
        ),
        migrations.AddField(
            model_name='summaries',
            name='appraisal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='summary_appraisal', to='A_dbms.Appraisals', verbose_name='审保会'),
        ),
        migrations.AddField(
            model_name='summaries',
            name='article',
            field=models.OneToOneField(on_delete=django.db.models.deletion.PROTECT, related_name='summary_article', to='A_dbms.Customes', verbose_name='审保会'),
        ),
    ]