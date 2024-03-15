# Generated by Django 4.2.1 on 2023-05-20 02:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('library', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='formstreamyear',
            name='teacher',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='column',
            name='row',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.row'),
        ),
        migrations.AddField(
            model_name='borrowed',
            name='book',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='library.book'),
        ),
        migrations.AddField(
            model_name='borrowed',
            name='librarian',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='borrowed',
            name='student',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.student'),
        ),
        migrations.AddField(
            model_name='book',
            name='column',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='library.column'),
        ),
    ]
