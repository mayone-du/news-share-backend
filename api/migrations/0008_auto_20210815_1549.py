# Generated by Django 3.2.5 on 2021-08-15 06:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0007_auto_20210702_2317'),
    ]

    operations = [
        migrations.AlterField(
            model_name='news',
            name='summary',
            field=models.CharField(blank=True, default='', max_length=500, null=True),
        ),
        migrations.AlterField(
            model_name='news',
            name='title',
            field=models.CharField(blank=True, default='', max_length=500, null=True),
        ),
    ]
