# SPDX-License-Identifier: AGPL-3.0-or-later
"""Native database-server source-of-truth models. ``DatabaseServer`` is the anchor: an engine
instance on a ``dcim.Device`` **or** a ``virtualization.VirtualMachine`` (exactly one), optionally
linked to the ``netbox_services.ServiceInstance`` that deployed it. Its tuned config surface is a
per-server 1:1 (``MariaDBConfig`` / ``PostgresConfig``), and the logical objects on it
(``Database`` / ``DatabaseUser`` / ``DatabaseGrant``) plus the engine-native HA clusters
(``GaleraCluster`` / ``PostgresCluster`` and their nodes) hang off it.

FKs to core/sibling models use STRING labels ("dcim.Device", "virtualization.VirtualMachine",
"netbox_services.ServiceInstance") — never import those into this module.

SECRET POLICY: a database password is NEVER a field here. ``DatabaseUser.credential_ref`` is an
OpenBao path reference (the netbox-services convention); the secret value stays in OpenBao.

CONFIG SEMANTICS: the nullable typed fields on ``MariaDBConfig`` / ``PostgresConfig`` mean "let the
engine default apply" when NULL — a set value overrides. This mirrors the netbox-zfs settable-field
precedent (NULL = inherited/default, a real value = explicit).
"""
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from netbox.models import NetBoxModel
from .choices import (
    DatabaseEngineChoices, GaleraSSTMethodChoices, PostgresHAModeChoices, PostgresRoleChoices,
)

# Engines that share the MySQL wire protocol + my.cnf surface (MariaDBConfig, Galera).
MYSQL_FAMILY_ENGINES = (DatabaseEngineChoices.MARIADB, DatabaseEngineChoices.MYSQL)


class DatabaseServer(NetBoxModel):
    """A single relational database engine instance. Installed onto exactly one of a raw-OS
    ``dcim.Device`` or a ``virtualization.VirtualMachine`` (enforced by :meth:`clean`), optionally
    the ``netbox_services.ServiceInstance`` it was deployed as. ``version`` is the apt/pkg target
    (e.g. ``10.11`` for MariaDB, ``16`` for PostgreSQL)."""

    name = models.CharField(max_length=100, unique=True)
    engine = models.CharField(max_length=16, choices=DatabaseEngineChoices)
    version = models.CharField(max_length=32, help_text="Engine version target (e.g. 10.11, 16).")
    port = models.PositiveIntegerField(help_text="TCP listen port (3306 MySQL family, 5432 Postgres).")
    listen_address = models.CharField(
        max_length=255, default="0.0.0.0", help_text="Bind address / listen_addresses."
    )
    data_dir = models.CharField(max_length=255, blank=True, help_text="On-disk data directory.")
    on_zfs = models.BooleanField(
        default=False, help_text="Data dir is ZFS-backed (drives the COW-aware config knobs)."
    )
    device = models.ForeignKey(
        "dcim.Device", on_delete=models.CASCADE, null=True, blank=True,
        related_name="database_servers",
    )
    virtual_machine = models.ForeignKey(
        "virtualization.VirtualMachine", on_delete=models.CASCADE, null=True, blank=True,
        related_name="database_servers",
    )
    service_instance = models.ForeignKey(
        "netbox_services.ServiceInstance", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="database_servers",
        help_text="The netbox-services instance this server was deployed as (composition link).",
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Database Server"

    def __str__(self):
        return f"{self.name} ({self.engine} {self.version})"

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:databaseserver", args=[self.pk])

    def get_engine_color(self):
        return DatabaseEngineChoices.colors.get(self.engine)

    @property
    def host(self):
        """The install target — the device or the VM, whichever is set."""
        return self.device or self.virtual_machine

    def clean(self):
        super().clean()
        if bool(self.device_id) == bool(self.virtual_machine_id):
            raise ValidationError("Set exactly one of device or virtual_machine as the host.")


class MariaDBConfig(NetBoxModel):
    """Per-server MariaDB/MySQL tuning (the managed ``99-ansible.cnf`` surface). Every field is
    nullable: NULL = let the engine default apply, a value = explicit override. The ZFS-only knobs
    (``innodb_doublewrite``, ``innodb_flush_method``) are emitted only when the server is on ZFS."""

    server = models.OneToOneField(
        DatabaseServer, on_delete=models.CASCADE, related_name="mariadb_config"
    )
    innodb_buffer_pool_size = models.CharField(
        max_length=32, null=True, blank=True, help_text="e.g. 128M, 4G (NULL = engine default)."
    )
    max_connections = models.PositiveIntegerField(null=True, blank=True)
    character_set_server = models.CharField(max_length=64, default="utf8mb4")
    collation_server = models.CharField(max_length=64, default="utf8mb4_unicode_ci")
    innodb_doublewrite = models.BooleanField(
        null=True, blank=True, help_text="ZFS COW: set 0 to skip the redundant doublewrite buffer."
    )
    innodb_flush_method = models.CharField(
        max_length=32, null=True, blank=True, help_text="ZFS COW: fsync (avoid O_DIRECT vs ARC)."
    )
    bind_address = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="my.cnf bind-address override (NULL = use the server's listen_address).",
    )

    class Meta:
        ordering = ["server"]
        verbose_name = "MariaDB Config"

    def __str__(self):
        return f"MariaDB config: {self.server}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:mariadbconfig", args=[self.pk])


class PostgresConfig(NetBoxModel):
    """Per-server PostgreSQL tuning (the managed ``postgresql.conf`` surface). Sizing fields are
    nullable (NULL = engine default). The ZFS-only WAL knobs (``wal_init_zero``, ``wal_recycle``
    off) are emitted only when the server is on ZFS; ``password_encryption`` defaults to
    ``scram-sha-256`` to match the pg_hba policy."""

    server = models.OneToOneField(
        DatabaseServer, on_delete=models.CASCADE, related_name="postgres_config"
    )
    shared_buffers = models.CharField(max_length=32, null=True, blank=True)
    effective_cache_size = models.CharField(max_length=32, null=True, blank=True)
    work_mem = models.CharField(max_length=32, null=True, blank=True)
    maintenance_work_mem = models.CharField(max_length=32, null=True, blank=True)
    max_connections = models.PositiveIntegerField(null=True, blank=True)
    wal_init_zero = models.BooleanField(
        null=True, blank=True, help_text="ZFS COW: set off to skip WAL pre-allocation zeroing."
    )
    wal_recycle = models.BooleanField(
        null=True, blank=True, help_text="ZFS COW: set off to skip WAL segment recycling."
    )
    password_encryption = models.CharField(max_length=32, default="scram-sha-256")
    listen_addresses = models.CharField(max_length=255, default="*")

    class Meta:
        ordering = ["server"]
        verbose_name = "Postgres Config"

    def __str__(self):
        return f"Postgres config: {self.server}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:postgresconfig", args=[self.pk])


class Database(NetBoxModel):
    """A logical database on a server. The provider CRUDs the database object itself (via the
    composed cyrilgdn/postgresql or petoju/mysql community provider); table schema is NOT modeled
    here — apps own that."""

    server = models.ForeignKey(DatabaseServer, on_delete=models.CASCADE, related_name="databases")
    name = models.CharField(max_length=100)
    owner = models.CharField(max_length=100, blank=True, help_text="Owning role/user (blank = default).")
    charset = models.CharField(max_length=64, blank=True)
    collation = models.CharField(max_length=64, blank=True)

    class Meta:
        ordering = ["server", "name"]
        verbose_name = "Database"
        constraints = [
            models.UniqueConstraint(
                fields=["server", "name"], name="netbox_database_database_unique_server_name"
            ),
        ]

    def __str__(self):
        return f"{self.server.name}: {self.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:database", args=[self.pk])


class DatabaseUser(NetBoxModel):
    """A login role on a server. ``host_scope`` is the MySQL host part (``%`` = any); Postgres
    ignores it. ``credential_ref`` is an OpenBao PATH — never the password value."""

    server = models.ForeignKey(DatabaseServer, on_delete=models.CASCADE, related_name="users")
    username = models.CharField(max_length=100)
    host_scope = models.CharField(
        max_length=255, default="%", help_text="MySQL host part ('%' = any); ignored for Postgres."
    )
    credential_ref = models.CharField(
        max_length=255, blank=True, help_text="OpenBao path for the password — NEVER the secret."
    )

    class Meta:
        ordering = ["server", "username", "host_scope"]
        verbose_name = "Database User"
        constraints = [
            models.UniqueConstraint(
                fields=["server", "username", "host_scope"],
                name="netbox_database_databaseuser_unique_server_username_host",
            ),
        ]

    def __str__(self):
        return f"{self.server.name}: {self.username}@{self.host_scope}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:databaseuser", args=[self.pk])


class DatabaseGrant(NetBoxModel):
    """A privilege grant of one user on one database. ``privileges`` is the engine-native grant
    string (e.g. ``ALL``, ``SELECT,INSERT``, ``ALL PRIVILEGES``)."""

    user = models.ForeignKey(DatabaseUser, on_delete=models.CASCADE, related_name="grants")
    database = models.ForeignKey(Database, on_delete=models.CASCADE, related_name="grants")
    privileges = models.CharField(max_length=255, help_text="Engine-native grant string (e.g. ALL).")

    class Meta:
        ordering = ["user", "database"]
        verbose_name = "Database Grant"
        constraints = [
            models.UniqueConstraint(
                fields=["user", "database"], name="netbox_database_databasegrant_unique_user_database"
            ),
        ]

    def __str__(self):
        return f"{self.user.username}@{self.database.name}: {self.privileges}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:databasegrant", args=[self.pk])


class GaleraCluster(NetBoxModel):
    """A MariaDB/MySQL Galera (write-set) synchronous cluster. Models the database-native
    multi-primary replication that ``netbox_services.HAMirror`` (async fail-over pairing) cannot
    express — the two are complementary, not duplicates."""

    name = models.CharField(max_length=100, unique=True)
    sst_method = models.CharField(
        max_length=16, choices=GaleraSSTMethodChoices, default=GaleraSSTMethodChoices.MARIABACKUP
    )
    cluster_address = models.CharField(
        max_length=255, blank=True, help_text="gcomm:// cluster address (blank on the bootstrap)."
    )

    class Meta:
        ordering = ["name"]
        verbose_name = "Galera Cluster"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:galeracluster", args=[self.pk])

    def get_sst_method_color(self):
        return GaleraSSTMethodChoices.colors.get(self.sst_method)


class GaleraNode(NetBoxModel):
    """A server's membership in a Galera cluster. The server must be a MySQL-family engine
    (:meth:`clean`). ``is_bootstrap`` marks the node that starts the cluster; ``segment`` groups
    nodes for WAN-optimized replication."""

    cluster = models.ForeignKey(GaleraCluster, on_delete=models.CASCADE, related_name="nodes")
    server = models.OneToOneField(
        DatabaseServer, on_delete=models.CASCADE, related_name="galera_node"
    )
    node_address = models.CharField(max_length=255, help_text="wsrep_node_address for this member.")
    is_bootstrap = models.BooleanField(default=False)
    segment = models.PositiveIntegerField(default=0, help_text="gmcast.segment for WAN grouping.")

    class Meta:
        ordering = ["cluster", "node_address"]
        verbose_name = "Galera Node"

    def __str__(self):
        return f"{self.cluster.name}: {self.server.name}"

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:galeranode", args=[self.pk])

    def clean(self):
        super().clean()
        if self.server_id and self.server.engine not in MYSQL_FAMILY_ENGINES:
            raise ValidationError("A Galera node requires a MariaDB or MySQL server engine.")


class PostgresCluster(NetBoxModel):
    """A PostgreSQL high-availability cluster. ``ha_mode`` selects the orchestrator (Patroni /
    repmgr / bare streaming); ``dcs_reference`` names the distributed config store (etcd/consul)
    for Patroni; ``synchronous`` toggles synchronous_commit-backed standbys."""

    name = models.CharField(max_length=100, unique=True)
    ha_mode = models.CharField(max_length=16, choices=PostgresHAModeChoices)
    dcs_reference = models.CharField(
        max_length=255, blank=True, help_text="DCS name/endpoint (etcd/consul) — Patroni."
    )
    synchronous = models.BooleanField(default=False, help_text="Use synchronous standbys.")

    class Meta:
        ordering = ["name"]
        verbose_name = "Postgres Cluster"

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:postgrescluster", args=[self.pk])

    def get_ha_mode_color(self):
        return PostgresHAModeChoices.colors.get(self.ha_mode)


class PostgresClusterNode(NetBoxModel):
    """A server's membership in a PostgreSQL cluster. The server must be a PostgreSQL engine
    (:meth:`clean`). ``role`` is the replication role; ``replication_slot`` names the slot the
    primary keeps for this standby; ``is_synchronous_standby`` marks a member of the sync set."""

    cluster = models.ForeignKey(PostgresCluster, on_delete=models.CASCADE, related_name="nodes")
    server = models.OneToOneField(
        DatabaseServer, on_delete=models.CASCADE, related_name="postgres_cluster_node"
    )
    role = models.CharField(max_length=16, choices=PostgresRoleChoices)
    replication_slot = models.CharField(max_length=100, blank=True)
    is_synchronous_standby = models.BooleanField(default=False)

    class Meta:
        ordering = ["cluster", "role", "server"]
        verbose_name = "Postgres Cluster Node"

    def __str__(self):
        return f"{self.cluster.name}: {self.server.name} ({self.role})"

    def get_absolute_url(self):
        return reverse("plugins:netbox_database:postgresclusternode", args=[self.pk])

    def get_role_color(self):
        return PostgresRoleChoices.colors.get(self.role)

    def clean(self):
        super().clean()
        if self.server_id and self.server.engine != DatabaseEngineChoices.POSTGRESQL:
            raise ValidationError("A Postgres cluster node requires a PostgreSQL server engine.")
