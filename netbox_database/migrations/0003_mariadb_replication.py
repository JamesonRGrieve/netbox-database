# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored incremental migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_database --check --dry-run   (on a dev/ephemeral NetBox)
# Adds MariaDB/MySQL binlog-replication HA (MariaDBReplication group + per-server
# MariaDBReplicationNode), the async/semi-sync master-master|master-slave topology Galera (synchronous
# write-set) and netbox_services.HAMirror (service-level pairing) cannot express. The node is a
# per-server 1:1 to netbox_database.DatabaseServer (0001_initial); the topology/sync/role additions to
# the ChoiceSets need no migration — choices are not DB-enforced.
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
        ("netbox_database", "0002_mongodb_redis_mosquitto_configs"),
    ]
    operations = [
        migrations.CreateModel(
            name="MariaDBReplication",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=100, unique=True)),
                ("topology", models.CharField(max_length=16)),
                ("sync_mode", models.CharField(default="async", max_length=16)),
                ("gtid", models.BooleanField(default=True)),
                ("ssl", models.BooleanField(default=False)),
                _TAGS,
            ],
            options={"verbose_name": "MariaDB Replication", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="MariaDBReplicationNode",
            fields=[
                *_BASE,
                ("mariadb_server_id", models.PositiveIntegerField()),
                ("role", models.CharField(max_length=16)),
                ("read_only", models.BooleanField(default=False)),
                ("replication", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="nodes", to="netbox_database.mariadbreplication")),
                ("server", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="mariadb_replication_node", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={"verbose_name": "MariaDB Replication Node", "ordering": ["replication", "role", "server"]},
        ),
        migrations.AddConstraint(
            model_name="mariadbreplicationnode",
            constraint=models.UniqueConstraint(
                fields=["replication", "mariadb_server_id"], name="unique_replication_mariadb_server_id"
            ),
        ),
    ]
