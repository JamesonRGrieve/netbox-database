# SPDX-License-Identifier: AGPL-3.0-or-later
import django_tables2 as tables
from netbox.tables import NetBoxTable, columns
from .models import (
    Database, DatabaseGrant, DatabaseServer, DatabaseUser, GaleraCluster, GaleraNode,
    MariaDBConfig, MariaDBReplication, MariaDBReplicationNode, MongoDBConfig, MosquittoConfig,
    PostgresCluster, PostgresClusterNode, PostgresConfig, RedisConfig,
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


class MongoDBConfigTable(NetBoxTable):
    server = tables.Column(linkify=True)
    storage_engine = columns.ChoiceFieldColumn()
    auth_enabled = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:mongodbconfig_list")

    class Meta(NetBoxTable.Meta):
        model = MongoDBConfig
        fields = ("pk", "id", "server", "storage_engine", "cache_size_gb", "repl_set_name", "bind_ip",
                  "auth_enabled", "tags", "created", "last_updated")
        default_columns = ("server", "storage_engine", "cache_size_gb", "repl_set_name")


class RedisConfigTable(NetBoxTable):
    server = tables.Column(linkify=True)
    maxmemory_policy = columns.ChoiceFieldColumn()
    appendonly = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:redisconfig_list")

    class Meta(NetBoxTable.Meta):
        model = RedisConfig
        fields = ("pk", "id", "server", "maxmemory", "maxmemory_policy", "appendonly", "save_rule",
                  "databases", "requirepass_ref", "tags", "created", "last_updated")
        default_columns = ("server", "maxmemory", "maxmemory_policy", "appendonly")


class MosquittoConfigTable(NetBoxTable):
    server = tables.Column(linkify=True)
    persistence = columns.ChoiceFieldColumn()
    allow_anonymous = columns.BooleanColumn()
    tls_enabled = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:mosquittoconfig_list")

    class Meta(NetBoxTable.Meta):
        model = MosquittoConfig
        fields = ("pk", "id", "server", "persistence", "allow_anonymous", "max_connections",
                  "password_file_ref", "tls_enabled", "tags", "created", "last_updated")
        default_columns = ("server", "persistence", "allow_anonymous", "tls_enabled")


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


class MariaDBReplicationTable(NetBoxTable):
    name = tables.Column(linkify=True)
    topology = columns.ChoiceFieldColumn()
    sync_mode = columns.ChoiceFieldColumn()
    gtid = columns.BooleanColumn()
    ssl = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:mariadbreplication_list")

    class Meta(NetBoxTable.Meta):
        model = MariaDBReplication
        fields = ("pk", "id", "name", "topology", "sync_mode", "gtid", "ssl", "tags", "created", "last_updated")
        default_columns = ("name", "topology", "sync_mode", "gtid")


class MariaDBReplicationNodeTable(NetBoxTable):
    replication = tables.Column(linkify=True)
    server = tables.Column(linkify=True)
    role = columns.ChoiceFieldColumn()
    read_only = columns.BooleanColumn()
    tags = columns.TagColumn(url_name="plugins:netbox_database:mariadbreplicationnode_list")

    class Meta(NetBoxTable.Meta):
        model = MariaDBReplicationNode
        fields = ("pk", "id", "replication", "server", "mariadb_server_id", "role", "read_only", "tags", "created", "last_updated")
        default_columns = ("replication", "server", "mariadb_server_id", "role", "read_only")
