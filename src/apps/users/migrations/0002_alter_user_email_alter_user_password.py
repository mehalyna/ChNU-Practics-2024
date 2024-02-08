# Generated by Django 4.2.9 on 2024-02-07 23:03

from django.db import migrations
from django.db import models


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="email",
            field=models.EmailField(
                max_length=50, unique=True, verbose_name="Email Address"
            ),
        ),
        migrations.AlterField(
            model_name="user",
            name="password",
            field=models.CharField(max_length=100, verbose_name="Password"),
        ),
    ]
