# Generated by Django 3.0.4 on 2020-12-11 17:04

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0002_alter_domain_unique"),
        ("community", "0004_make_community_mandatory"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommunitySite",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("datetime_created", models.DateTimeField(auto_now_add=True)),
                ("datetime_updated", models.DateTimeField(auto_now=True)),
                (
                    "discord_url",
                    models.CharField(blank=True, max_length=512, null=True),
                ),
                (
                    "community",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="sites",
                        to="community.Community",
                    ),
                ),
                (
                    "site",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="community",
                        to="sites.Site",
                    ),
                ),
            ],
            options={
                "verbose_name": "community site",
                "verbose_name_plural": "community sites",
            },
        ),
    ]
