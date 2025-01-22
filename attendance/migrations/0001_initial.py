# Generated by Django 3.2.25 on 2025-01-22 13:37

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('check_in', models.DateTimeField(blank=True, null=True)),
                ('check_out', models.DateTimeField(blank=True, null=True)),
                ('lateness', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('not_working_day', 'Not Working Day'), ('not_working_hour', 'Not Working Hour'), ('not_checked_in', 'Not Checked In'), ('checked_in', 'Checked In'), ('checked_out', 'Checked Out'), ('on_leave', 'On Leave')], default='not_checked_in', max_length=20)),
            ],
        ),
    ]
