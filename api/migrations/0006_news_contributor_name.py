# Generated by Django 3.2.4 on 2021-06-29 07:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_news_image_path'),
    ]

    operations = [
        migrations.AddField(
            model_name='news',
            name='contributor_name',
            field=models.CharField(blank=True, default='', max_length=50, null=True),
        ),
    ]