# Generated by Django 3.2.25 on 2025-01-15 14:30

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('type', models.CharField(choices=[('persistent', 'Persistent'), ('temporary', 'Temporary')], default='temporary', max_length=20)),
                ('severity', models.CharField(choices=[('success', 'Success'), ('warning', 'Warning'), ('info', 'Info'), ('danger', 'Danger')], default='info', max_length=20)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
