# Generated by Django 4.2.11 on 2024-05-26 18:26

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraccount',
            name='otp',
            field=models.CharField(blank=True, max_length=6, null=True),
        ),
    ]