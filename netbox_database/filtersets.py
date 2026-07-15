# SPDX-License-Identifier: AGPL-3.0-or-later
import django_filters
from dcim.models import Device
from django.db.models import Q
from netbox.filtersets import NetBoxModelFilterSet
from virtualization.models import VirtualMachine
from .choices import (
    DatabaseEngineChoices, GaleraSSTMethodChoices, MariaDBReplicationRoleChoices,
    MariaDBReplicationSyncChoices, MariaDBReplicationTopologyChoices, MongoStorageEngineChoices,
    MosquittoPersistenceChoices, PostgresHAModeChoices, PostgresRoleChoices,
    RedisMaxmemoryPolicyChoices,
)
from .models import (
    Database, DatabaseGrant, DatabaseServer, DatabaseUser, GaleraCluster, GaleraNode,
    MariaDBConfig, MariaDBReplication, MariaDBReplicationNode, MongoDBConfig, MosquittoConfig,
    PostgresCluster, PostgresClusterNode, PostgresConfig, RedisConfig,
)

# Explicit FK filters: django-filter does NOT derive `<fk>_id` from a bare FK in Meta.fields, so
# `?server_id=` would be silently ignored. NetBox convention is `<fk>_id` (by PK) + `<fk>` (name).


class _ServerFilterMixin(NetBoxModelFilterSet):
    server_id = django_filters.ModelMultipleChoiceFilter(
        field_name="server", queryset=DatabaseServer.objects.all(), label="Server (ID)"
    )
    server = django_filters.ModelMultipleChoiceFilter(
        field_name="server__name", to_field_name="name", queryset=DatabaseServer.objects.all(),
        label="Server (name)",
    )

    class Meta:
        abstract = True


class DatabaseServerFilterSet(NetBoxModelFilterSet):
    engine = django_filters.MultipleChoiceFilter(choices=DatabaseEngineChoices)
    device_id = django_filters.ModelMultipleChoiceFilter(
        field_name="device", queryset=Device.objects.all(), label="Device (ID)"
    )
    virtual_machine_id = django_filters.ModelMultipleChoiceFilter(
        field_name="virtual_machine", queryset=VirtualMachine.objects.all(), label="VM (ID)"
    )

    class Meta:
        model = DatabaseServer
        fields = ["id", "name", "version", "port", "listen_address", "data_dir", "on_zfs", "service_instance_id"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(version__icontains=value)
            | Q(listen_address__icontains=value) | Q(data_dir__icontains=value)
        )


class MariaDBConfigFilterSet(_ServerFilterMixin):
    class Meta:
        model = MariaDBConfig
        fields = ["id", "innodb_buffer_pool_size", "max_connections", "character_set_server",
                  "collation_server", "innodb_doublewrite", "innodb_flush_method", "bind_address"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(server__name__icontains=value))


class PostgresConfigFilterSet(_ServerFilterMixin):
    class Meta:
        model = PostgresConfig
        fields = ["id", "shared_buffers", "effective_cache_size", "work_mem", "maintenance_work_mem",
                  "max_connections", "wal_init_zero", "wal_recycle", "password_encryption", "listen_addresses"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(server__name__icontains=value))


class MongoDBConfigFilterSet(_ServerFilterMixin):
    storage_engine = django_filters.MultipleChoiceFilter(choices=MongoStorageEngineChoices)

    class Meta:
        model = MongoDBConfig
        fields = ["id", "cache_size_gb", "repl_set_name", "bind_ip", "auth_enabled"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(server__name__icontains=value) | Q(repl_set_name__icontains=value))


class RedisConfigFilterSet(_ServerFilterMixin):
    maxmemory_policy = django_filters.MultipleChoiceFilter(choices=RedisMaxmemoryPolicyChoices)

    class Meta:
        model = RedisConfig
        fields = ["id", "maxmemory", "appendonly", "save_rule", "databases", "requirepass_ref"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(server__name__icontains=value) | Q(maxmemory__icontains=value))


class MosquittoConfigFilterSet(_ServerFilterMixin):
    persistence = django_filters.MultipleChoiceFilter(choices=MosquittoPersistenceChoices)

    class Meta:
        model = MosquittoConfig
        fields = ["id", "allow_anonymous", "max_connections", "password_file_ref", "tls_enabled"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(server__name__icontains=value))


class DatabaseFilterSet(_ServerFilterMixin):
    class Meta:
        model = Database
        fields = ["id", "name", "owner", "charset", "collation"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(name__icontains=value) | Q(owner__icontains=value) | Q(server__name__icontains=value)
        )


class DatabaseUserFilterSet(_ServerFilterMixin):
    class Meta:
        model = DatabaseUser
        fields = ["id", "username", "host_scope", "credential_ref"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(username__icontains=value) | Q(host_scope__icontains=value)
            | Q(server__name__icontains=value)
        )


class DatabaseGrantFilterSet(NetBoxModelFilterSet):
    user_id = django_filters.ModelMultipleChoiceFilter(
        field_name="user", queryset=DatabaseUser.objects.all(), label="User (ID)"
    )
    database_id = django_filters.ModelMultipleChoiceFilter(
        field_name="database", queryset=Database.objects.all(), label="Database (ID)"
    )

    class Meta:
        model = DatabaseGrant
        fields = ["id", "privileges"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(privileges__icontains=value) | Q(user__username__icontains=value)
            | Q(database__name__icontains=value)
        )


class GaleraClusterFilterSet(NetBoxModelFilterSet):
    sst_method = django_filters.MultipleChoiceFilter(choices=GaleraSSTMethodChoices)

    class Meta:
        model = GaleraCluster
        fields = ["id", "name", "cluster_address"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(cluster_address__icontains=value))


class GaleraNodeFilterSet(_ServerFilterMixin):
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name="cluster", queryset=GaleraCluster.objects.all(), label="Cluster (ID)"
    )

    class Meta:
        model = GaleraNode
        fields = ["id", "node_address", "is_bootstrap", "segment"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(node_address__icontains=value) | Q(cluster__name__icontains=value)
            | Q(server__name__icontains=value)
        )


class PostgresClusterFilterSet(NetBoxModelFilterSet):
    ha_mode = django_filters.MultipleChoiceFilter(choices=PostgresHAModeChoices)

    class Meta:
        model = PostgresCluster
        fields = ["id", "name", "dcs_reference", "synchronous"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value) | Q(dcs_reference__icontains=value))


class PostgresClusterNodeFilterSet(_ServerFilterMixin):
    cluster_id = django_filters.ModelMultipleChoiceFilter(
        field_name="cluster", queryset=PostgresCluster.objects.all(), label="Cluster (ID)"
    )
    role = django_filters.MultipleChoiceFilter(choices=PostgresRoleChoices)

    class Meta:
        model = PostgresClusterNode
        fields = ["id", "replication_slot", "is_synchronous_standby"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(cluster__name__icontains=value) | Q(server__name__icontains=value)
            | Q(replication_slot__icontains=value)
        )


class MariaDBReplicationFilterSet(NetBoxModelFilterSet):
    topology = django_filters.MultipleChoiceFilter(choices=MariaDBReplicationTopologyChoices)
    sync_mode = django_filters.MultipleChoiceFilter(choices=MariaDBReplicationSyncChoices)

    class Meta:
        model = MariaDBReplication
        fields = ["id", "name", "gtid", "ssl"]

    def search(self, queryset, name, value):
        return queryset.filter(Q(name__icontains=value))


class MariaDBReplicationNodeFilterSet(_ServerFilterMixin):
    replication_id = django_filters.ModelMultipleChoiceFilter(
        field_name="replication", queryset=MariaDBReplication.objects.all(), label="Replication (ID)"
    )
    role = django_filters.MultipleChoiceFilter(choices=MariaDBReplicationRoleChoices)

    class Meta:
        model = MariaDBReplicationNode
        fields = ["id", "mariadb_server_id", "read_only"]

    def search(self, queryset, name, value):
        return queryset.filter(
            Q(replication__name__icontains=value) | Q(server__name__icontains=value)
        )
