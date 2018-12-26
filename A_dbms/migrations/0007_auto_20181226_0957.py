# Generated by Django 2.1.3 on 2018-12-26 01:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('A_dbms', '0006_auto_20181226_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='lendingorder',
            name='order',
            field=models.IntegerField(choices=[(1, '第一次'), (2, '第二次'), (3, '第三次'), (4, '第四次')], default=1, verbose_name='发放次序'),
        ),
        migrations.AlterUniqueTogether(
            name='lendingorder',
            unique_together={('summary', 'order')},
        ),
    ]
