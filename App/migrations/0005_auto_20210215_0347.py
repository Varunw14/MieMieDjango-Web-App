# Generated by Django 3.1.6 on 2021-02-15 03:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('App', '0004_auto_20210215_0345'),
    ]

    operations = [
        migrations.AlterField(
            model_name='module',
            name='Module_Lead',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
