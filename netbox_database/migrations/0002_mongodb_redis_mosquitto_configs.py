# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored incremental migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_database --check --dry-run   (on a dev/ephemeral NetBox)
# Adds the three non-SQL server-config models (MongoDBConfig / RedisConfig / MosquittoConfig), each a
# per-server 1:1 to netbox_database.DatabaseServer (0001_initial). The DatabaseEngineChoices additions
# (mongodb/redis/valkey/mosquitto) need no migration — choices are not DB-enforced.
import django.db.models.deletion
import taggit.managers
import utilities.json
from django.db import migrations, models

_BASE = [
    ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False)),
    ("created", models.DateTimeField(auto_now_add=True, blank=True, null=True)),
    ("last_updated", models.DateTimeField(auto_now=True, blank=True, null=True)),
    ("custom_field_data", models.JSONField(blank=True, default=dict, encoder=utilities.json.CustomFieldJSONEncoder)),
]
_TAGS = ("tags", taggit.managers.TaggableManager(through="extras.TaggedItem", to="extras.Tag"))


class Migration(migrations.Migration):
    dependencies = [
        ("netbox_database", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="MongoDBConfig",
            fields=[
                *_BASE,
                ("storage_engine", models.CharField(default="wiredTiger", max_length=16)),
                ("cache_size_gb", models.DecimalField(blank=True, decimal_places=2, max_digits=6, null=True)),
                ("repl_set_name", models.CharField(blank=True, max_length=100)),
                ("bind_ip", models.CharField(default="0.0.0.0", max_length=255)),
                ("auth_enabled", models.BooleanField(default=True)),
                ("server", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="mongodb_config", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={"verbose_name": "MongoDB Config", "ordering": ["server"]},
        ),
        migrations.CreateModel(
            name="RedisConfig",
            fields=[
                *_BASE,
                ("maxmemory", models.CharField(blank=True, max_length=32)),
                ("maxmemory_policy", models.CharField(default="noeviction", max_length=16)),
                ("appendonly", models.BooleanField(default=False)),
                ("save_rule", models.CharField(blank=True, max_length=255)),
                ("databases", models.PositiveIntegerField(default=16)),
                ("requirepass_ref", models.CharField(blank=True, max_length=255)),
                ("server", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="redis_config", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={"verbose_name": "Redis Config", "ordering": ["server"]},
        ),
        migrations.CreateModel(
            name="MosquittoConfig",
            fields=[
                *_BASE,
                ("persistence", models.CharField(default="file", max_length=16)),
                ("allow_anonymous", models.BooleanField(default=False)),
                ("max_connections", models.IntegerField(default=-1)),
                ("password_file_ref", models.CharField(blank=True, max_length=255)),
                ("tls_enabled", models.BooleanField(default=False)),
                ("server", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="mosquitto_config", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={"verbose_name": "Mosquitto Config", "ordering": ["server"]},
        ),
    ]
