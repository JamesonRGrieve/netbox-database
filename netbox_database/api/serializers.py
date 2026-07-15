# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.api.serializers import DeviceSerializer
from netbox.api.serializers import NetBoxModelSerializer
from netbox_services.api.serializers import ServiceInstanceSerializer
from rest_framework import serializers
from virtualization.api.serializers import VirtualMachineSerializer
from ..models import (
    Database, DatabaseGrant, DatabaseServer, DatabaseUser, GaleraCluster, GaleraNode,
    MariaDBConfig, MariaDBReplication, MariaDBReplicationNode, MongoDBConfig, MosquittoConfig,
    PostgresCluster, PostgresClusterNode,
    PostgresConfig, RedisConfig,
)


class DatabaseServerSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:databaseserver-detail")
    device = DeviceSerializer(nested=True, required=False, allow_null=True)
    virtual_machine = VirtualMachineSerializer(nested=True, required=False, allow_null=True)
    service_instance = ServiceInstanceSerializer(nested=True, required=False, allow_null=True)

    class Meta:
        model = DatabaseServer
        fields = [
            "id", "url", "display", "name", "engine", "version", "port", "listen_address", "data_dir",
            "on_zfs", "device", "virtual_machine", "service_instance",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "engine", "version"]


class MariaDBConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:mariadbconfig-detail")
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = MariaDBConfig
        fields = [
            "id", "url", "display", "server", "innodb_buffer_pool_size", "max_connections",
            "character_set_server", "collation_server", "innodb_doublewrite", "innodb_flush_method",
            "bind_address", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "server"]


class PostgresConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:postgresconfig-detail")
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = PostgresConfig
        fields = [
            "id", "url", "display", "server", "shared_buffers", "effective_cache_size", "work_mem",
            "maintenance_work_mem", "max_connections", "wal_init_zero", "wal_recycle",
            "password_encryption", "listen_addresses", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "server"]


class MongoDBConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:mongodbconfig-detail")
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = MongoDBConfig
        fields = [
            "id", "url", "display", "server", "storage_engine", "cache_size_gb", "repl_set_name",
            "bind_ip", "auth_enabled", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "server"]


class RedisConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:redisconfig-detail")
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = RedisConfig
        fields = [
            "id", "url", "display", "server", "maxmemory", "maxmemory_policy", "appendonly",
            "save_rule", "databases", "requirepass_ref", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "server"]


class MosquittoConfigSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:mosquittoconfig-detail")
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = MosquittoConfig
        fields = [
            "id", "url", "display", "server", "persistence", "allow_anonymous", "max_connections",
            "password_file_ref", "tls_enabled", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "server"]


class DatabaseSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:database-detail")
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = Database
        fields = [
            "id", "url", "display", "server", "name", "owner", "charset", "collation",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "server", "name"]


class DatabaseUserSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:databaseuser-detail")
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = DatabaseUser
        fields = [
            "id", "url", "display", "server", "username", "host_scope", "credential_ref",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "server", "username"]


class DatabaseGrantSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:databasegrant-detail")
    user = DatabaseUserSerializer(nested=True)
    database = DatabaseSerializer(nested=True)

    class Meta:
        model = DatabaseGrant
        fields = [
            "id", "url", "display", "user", "database", "privileges",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "user", "database"]


class GaleraClusterSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:galeracluster-detail")

    class Meta:
        model = GaleraCluster
        fields = [
            "id", "url", "display", "name", "sst_method", "cluster_address",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "sst_method"]


class GaleraNodeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:galeranode-detail")
    cluster = GaleraClusterSerializer(nested=True)
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = GaleraNode
        fields = [
            "id", "url", "display", "cluster", "server", "node_address", "is_bootstrap", "segment",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "cluster", "server"]


class PostgresClusterSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:postgrescluster-detail")

    class Meta:
        model = PostgresCluster
        fields = [
            "id", "url", "display", "name", "ha_mode", "dcs_reference", "synchronous",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "ha_mode"]


class PostgresClusterNodeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:postgresclusternode-detail")
    cluster = PostgresClusterSerializer(nested=True)
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = PostgresClusterNode
        fields = [
            "id", "url", "display", "cluster", "server", "role", "replication_slot",
            "is_synchronous_standby", "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "cluster", "server", "role"]


class MariaDBReplicationSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:mariadbreplication-detail")

    class Meta:
        model = MariaDBReplication
        fields = [
            "id", "url", "display", "name", "topology", "sync_mode", "gtid", "ssl",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "name", "topology"]


class MariaDBReplicationNodeSerializer(NetBoxModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="plugins-api:netbox_database-api:mariadbreplicationnode-detail")
    replication = MariaDBReplicationSerializer(nested=True)
    server = DatabaseServerSerializer(nested=True)

    class Meta:
        model = MariaDBReplicationNode
        fields = [
            "id", "url", "display", "replication", "server", "mariadb_server_id", "role", "read_only",
            "tags", "custom_fields", "created", "last_updated",
        ]
        brief_fields = ["id", "url", "display", "replication", "server", "role"]
