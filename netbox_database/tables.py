# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import (
    Database, DatabaseGrant, DatabaseServer, DatabaseUser, GaleraCluster, GaleraNode,
    MariaDBConfig, PostgresCluster, PostgresClusterNode, PostgresConfig,
)


class DatabaseServerTable(NetBoxTable):
    name = tables.Column(linkify=True)
    engine = columns.ChoiceFieldColumn()
    device = tables.Column(linkify=True)
    virtual_machine = tables.Column(linkify=True)
    service_instance = tables.Column(linkify=True)
    on_zfs = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:databaseserver_list")

    class Meta(NetBoxTable.Meta):
        model = DatabaseServer
        fields = ("pk", "id", "name", "engine", "version", "port", "listen_address", "data_dir",
                  "on_zfs", "device", "virtual_machine", "service_instance", "tags", "created", "last_updated")
        default_columns = ("name", "engine", "version", "port", "device", "virtual_machine")


class MariaDBConfigTable(NetBoxTable):
    server = tables.Column(linkify=True)
    innodb_doublewrite = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:mariadbconfig_list")

    class Meta(NetBoxTable.Meta):
        model = MariaDBConfig
        fields = ("pk", "id", "server", "innodb_buffer_pool_size", "max_connections", "character_set_server",
                  "collation_server", "innodb_doublewrite", "innodb_flush_method", "bind_address", "tags", "created", "last_updated")
        default_columns = ("server", "innodb_buffer_pool_size", "max_connections", "character_set_server")


class PostgresConfigTable(NetBoxTable):
    server = tables.Column(linkify=True)
    wal_init_zero = columns.BooleanColumn()
    wal_recycle = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:postgresconfig_list")

    class Meta(NetBoxTable.Meta):
        model = PostgresConfig
        fields = ("pk", "id", "server", "shared_buffers", "effective_cache_size", "work_mem", "maintenance_work_mem",
                  "max_connections", "wal_init_zero", "wal_recycle", "password_encryption", "listen_addresses", "tags", "created", "last_updated")
        default_columns = ("server", "shared_buffers", "effective_cache_size", "max_connections")


class DatabaseTable(NetBoxTable):
    server = tables.Column(linkify=True)
    name = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_database:database_list")

    class Meta(NetBoxTable.Meta):
        model = Database
        fields = ("pk", "id", "server", "name", "owner", "charset", "collation", "tags", "created", "last_updated")
        default_columns = ("server", "name", "owner", "charset")


class DatabaseUserTable(NetBoxTable):
    server = tables.Column(linkify=True)
    username = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_database:databaseuser_list")

    class Meta(NetBoxTable.Meta):
        model = DatabaseUser
        fields = ("pk", "id", "server", "username", "host_scope", "credential_ref", "tags", "created", "last_updated")
        default_columns = ("server", "username", "host_scope", "credential_ref")


class DatabaseGrantTable(NetBoxTable):
    user = tables.Column(linkify=True)
    database = tables.Column(linkify=True)
    tags = columns.TagColumn(url_name="plugins:netbox_database:databasegrant_list")

    class Meta(NetBoxTable.Meta):
        model = DatabaseGrant
        fields = ("pk", "id", "user", "database", "privileges", "tags", "created", "last_updated")
        default_columns = ("user", "database", "privileges")


class GaleraClusterTable(NetBoxTable):
    name = tables.Column(linkify=True)
    sst_method = columns.ChoiceFieldColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:galeracluster_list")

    class Meta(NetBoxTable.Meta):
        model = GaleraCluster
        fields = ("pk", "id", "name", "sst_method", "cluster_address", "tags", "created", "last_updated")
        default_columns = ("name", "sst_method", "cluster_address")


class GaleraNodeTable(NetBoxTable):
    cluster = tables.Column(linkify=True)
    server = tables.Column(linkify=True)
    is_bootstrap = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:galeranode_list")

    class Meta(NetBoxTable.Meta):
        model = GaleraNode
        fields = ("pk", "id", "cluster", "server", "node_address", "is_bootstrap", "segment", "tags", "created", "last_updated")
        default_columns = ("cluster", "server", "node_address", "is_bootstrap")


class PostgresClusterTable(NetBoxTable):
    name = tables.Column(linkify=True)
    ha_mode = columns.ChoiceFieldColumn()
    synchronous = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:postgrescluster_list")

    class Meta(NetBoxTable.Meta):
        model = PostgresCluster
        fields = ("pk", "id", "name", "ha_mode", "dcs_reference", "synchronous", "tags", "created", "last_updated")
        default_columns = ("name", "ha_mode", "dcs_reference", "synchronous")


class PostgresClusterNodeTable(NetBoxTable):
    cluster = tables.Column(linkify=True)
    server = tables.Column(linkify=True)
    role = columns.ChoiceFieldColumn()
    is_synchronous_standby = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:postgresclusternode_list")

    class Meta(NetBoxTable.Meta):
        model = PostgresClusterNode
        fields = ("pk", "id", "cluster", "server", "role", "replication_slot", "is_synchronous_standby", "tags", "created", "last_updated")
        default_columns = ("cluster", "server", "role", "is_synchronous_standby")
