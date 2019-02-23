# Generated by Django 2.1.3 on 2019-02-23 05:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0004_standing'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='standing',
            options={'verbose_name_plural': '追偿-跟进台账'},
        ),
        migrations.AddField(
            model_name='dun',
            name='warrant',
            field=models.ManyToManyField(blank=True, null=True, related_name='dun_article', to='A_dbms.Warrants', verbose_name='资产线索'),
        ),
    ]
