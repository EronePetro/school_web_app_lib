# Generated by Django 4.2.1 on 2023-05-30 15:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('library', '0007_teacher'),
    ]

    operations = [
        migrations.AddField(
            model_name='borrowed',
            name='teacher',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='library.teacher'),
        ),
        migrations.AlterField(
            model_name='borrowed',
            name='student',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='library.student'),
        ),
    ]
