# Generated by Django 4.2.1 on 2023-05-31 02:48

from django.db import migrations
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0009_staff_remove_borrowed_teacher_delete_teacher_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='staff',
            name='contact',
            field=phonenumber_field.modelfields.PhoneNumberField(max_length=128, region=None),
        ),
    ]
