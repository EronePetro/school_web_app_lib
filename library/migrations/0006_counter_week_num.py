# Generated by Django 4.2.1 on 2023-05-26 03:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0005_counter'),
    ]

    operations = [
        migrations.AddField(
            model_name='counter',
            name='week_num',
            field=models.PositiveSmallIntegerField(default=0),
        ),
    ]
