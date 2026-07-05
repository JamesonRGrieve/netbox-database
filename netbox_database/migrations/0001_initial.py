# SPDX-License-Identifier: AGPL-3.0-or-later
# Hand-authored initial migration (NetBox disables makemigrations in production). Verify with:
#   python manage.py makemigrations netbox_database --check --dry-run   (on a dev/ephemeral NetBox)
# Re-confirm against the pinned NetBox 4.6: the DatabaseServer FK targets (dcim.device,
# virtualization.virtualmachine, netbox_services.serviceinstance) and the OneToOne config/node rows.
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
    initial = True
    dependencies = [
        ("dcim", "0001_initial"),
        ("extras", "0001_initial"),
        ("virtualization", "0001_initial"),
        # DatabaseServer.service_instance FKs netbox_services.ServiceInstance — its table must exist.
        ("netbox_services", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="DatabaseServer",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=100, unique=True)),
                ("engine", models.CharField(max_length=16)),
                ("version", models.CharField(max_length=32)),
                ("port", models.PositiveIntegerField()),
                ("listen_address", models.CharField(default="0.0.0.0", max_length=255)),
                ("data_dir", models.CharField(blank=True, max_length=255)),
                ("on_zfs", models.BooleanField(default=False)),
                ("device", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="database_servers", to="dcim.device")),
                ("virtual_machine", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name="database_servers", to="virtualization.virtualmachine")),
                ("service_instance", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="database_servers", to="netbox_services.serviceinstance")),
                _TAGS,
            ],
            options={"verbose_name": "Database Server", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="MariaDBConfig",
            fields=[
                *_BASE,
                ("innodb_buffer_pool_size", models.CharField(blank=True, max_length=32, null=True)),
                ("max_connections", models.PositiveIntegerField(blank=True, null=True)),
                ("character_set_server", models.CharField(default="utf8mb4", max_length=64)),
                ("collation_server", models.CharField(default="utf8mb4_unicode_ci", max_length=64)),
                ("innodb_doublewrite", models.BooleanField(blank=True, null=True)),
                ("innodb_flush_method", models.CharField(blank=True, max_length=32, null=True)),
                ("bind_address", models.CharField(blank=True, max_length=255, null=True)),
                ("server", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="mariadb_config", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={"verbose_name": "MariaDB Config", "ordering": ["server"]},
        ),
        migrations.CreateModel(
            name="PostgresConfig",
            fields=[
                *_BASE,
                ("shared_buffers", models.CharField(blank=True, max_length=32, null=True)),
                ("effective_cache_size", models.CharField(blank=True, max_length=32, null=True)),
                ("work_mem", models.CharField(blank=True, max_length=32, null=True)),
                ("maintenance_work_mem", models.CharField(blank=True, max_length=32, null=True)),
                ("max_connections", models.PositiveIntegerField(blank=True, null=True)),
                ("wal_init_zero", models.BooleanField(blank=True, null=True)),
                ("wal_recycle", models.BooleanField(blank=True, null=True)),
                ("password_encryption", models.CharField(default="scram-sha-256", max_length=32)),
                ("listen_addresses", models.CharField(default="*", max_length=255)),
                ("server", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="postgres_config", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={"verbose_name": "Postgres Config", "ordering": ["server"]},
        ),
        migrations.CreateModel(
            name="Database",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=100)),
                ("owner", models.CharField(blank=True, max_length=100)),
                ("charset", models.CharField(blank=True, max_length=64)),
                ("collation", models.CharField(blank=True, max_length=64)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="databases", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={
                "verbose_name": "Database",
                "ordering": ["server", "name"],
                "constraints": [models.UniqueConstraint(fields=("server", "name"), name="netbox_database_database_unique_server_name")],
            },
        ),
        migrations.CreateModel(
            name="DatabaseUser",
            fields=[
                *_BASE,
                ("username", models.CharField(max_length=100)),
                ("host_scope", models.CharField(default="%", max_length=255)),
                ("credential_ref", models.CharField(blank=True, max_length=255)),
                ("server", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="users", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={
                "verbose_name": "Database User",
                "ordering": ["server", "username", "host_scope"],
                "constraints": [models.UniqueConstraint(fields=("server", "username", "host_scope"), name="netbox_database_databaseuser_unique_server_username_host")],
            },
        ),
        migrations.CreateModel(
            name="DatabaseGrant",
            fields=[
                *_BASE,
                ("privileges", models.CharField(max_length=255)),
                ("database", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="grants", to="netbox_database.database")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="grants", to="netbox_database.databaseuser")),
                _TAGS,
            ],
            options={
                "verbose_name": "Database Grant",
                "ordering": ["user", "database"],
                "constraints": [models.UniqueConstraint(fields=("user", "database"), name="netbox_database_databasegrant_unique_user_database")],
            },
        ),
        migrations.CreateModel(
            name="GaleraCluster",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=100, unique=True)),
                ("sst_method", models.CharField(default="mariabackup", max_length=16)),
                ("cluster_address", models.CharField(blank=True, max_length=255)),
                _TAGS,
            ],
            options={"verbose_name": "Galera Cluster", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="GaleraNode",
            fields=[
                *_BASE,
                ("node_address", models.CharField(max_length=255)),
                ("is_bootstrap", models.BooleanField(default=False)),
                ("segment", models.PositiveIntegerField(default=0)),
                ("cluster", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="nodes", to="netbox_database.galeracluster")),
                ("server", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="galera_node", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={"verbose_name": "Galera Node", "ordering": ["cluster", "node_address"]},
        ),
        migrations.CreateModel(
            name="PostgresCluster",
            fields=[
                *_BASE,
                ("name", models.CharField(max_length=100, unique=True)),
                ("ha_mode", models.CharField(max_length=16)),
                ("dcs_reference", models.CharField(blank=True, max_length=255)),
                ("synchronous", models.BooleanField(default=False)),
                _TAGS,
            ],
            options={"verbose_name": "Postgres Cluster", "ordering": ["name"]},
        ),
        migrations.CreateModel(
            name="PostgresClusterNode",
            fields=[
                *_BASE,
                ("role", models.CharField(max_length=16)),
                ("replication_slot", models.CharField(blank=True, max_length=100)),
                ("is_synchronous_standby", models.BooleanField(default=False)),
                ("cluster", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="nodes", to="netbox_database.postgrescluster")),
                ("server", models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name="postgres_cluster_node", to="netbox_database.databaseserver")),
                _TAGS,
            ],
            options={"verbose_name": "Postgres Cluster Node", "ordering": ["cluster", "role", "server"]},
        ),
    ]
