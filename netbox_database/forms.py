# SPDX-License-Identifier: AGPL-3.0-or-later
from dcim.models import Device
from django import forms
from netbox.forms import NetBoxModelFilterSetForm, NetBoxModelForm
from utilities.forms.fields import DynamicModelChoiceField, DynamicModelMultipleChoiceField, TagFilterField
from utilities.forms.rendering import FieldSet
from virtualization.models import VirtualMachine
from .choices import (
    DatabaseEngineChoices, GaleraSSTMethodChoices, MongoStorageEngineChoices,
    MosquittoPersistenceChoices, PostgresHAModeChoices, PostgresRoleChoices,
    RedisMaxmemoryPolicyChoices,
)
from .models import (
    Database, DatabaseGrant, DatabaseServer, DatabaseUser, GaleraCluster, GaleraNode,
    MariaDBConfig, MongoDBConfig, MosquittoConfig, PostgresCluster, PostgresClusterNode,
    PostgresConfig, RedisConfig,
)


class DatabaseServerForm(NetBoxModelForm):
    device = DynamicModelChoiceField(queryset=Device.objects.all(), required=False)
    virtual_machine = DynamicModelChoiceField(queryset=VirtualMachine.objects.all(), required=False)

    fieldsets = (
        FieldSet("name", "engine", "version", name="Server"),
        FieldSet("port", "listen_address", "data_dir", "on_zfs", name="Listener / storage"),
        FieldSet("device", "virtual_machine", "service_instance", name="Host"),
    )

    class Meta:
        model = DatabaseServer
        fields = ["name", "engine", "version", "port", "listen_address", "data_dir", "on_zfs",
                  "device", "virtual_machine", "service_instance", "tags"]


class MariaDBConfigForm(NetBoxModelForm):
    server = DynamicModelChoiceField(queryset=DatabaseServer.objects.all())

    fieldsets = (
        FieldSet("server", "innodb_buffer_pool_size", "max_connections", "bind_address", name="MariaDB"),
        FieldSet("character_set_server", "collation_server", name="Charset"),
        FieldSet("innodb_doublewrite", "innodb_flush_method", name="ZFS tuning"),
    )

    class Meta:
        model = MariaDBConfig
        fields = ["server", "innodb_buffer_pool_size", "max_connections", "character_set_server",
                  "collation_server", "innodb_doublewrite", "innodb_flush_method", "bind_address", "tags"]


class PostgresConfigForm(NetBoxModelForm):
    server = DynamicModelChoiceField(queryset=DatabaseServer.objects.all())

    fieldsets = (
        FieldSet("server", "listen_addresses", "max_connections", "password_encryption", name="PostgreSQL"),
        FieldSet("shared_buffers", "effective_cache_size", "work_mem", "maintenance_work_mem", name="Sizing"),
        FieldSet("wal_init_zero", "wal_recycle", name="ZFS WAL tuning"),
    )

    class Meta:
        model = PostgresConfig
        fields = ["server", "shared_buffers", "effective_cache_size", "work_mem", "maintenance_work_mem",
                  "max_connections", "wal_init_zero", "wal_recycle", "password_encryption", "listen_addresses", "tags"]


class MongoDBConfigForm(NetBoxModelForm):
    server = DynamicModelChoiceField(queryset=DatabaseServer.objects.all())

    fieldsets = (
        FieldSet("server", "storage_engine", "cache_size_gb", "bind_ip", name="MongoDB"),
        FieldSet("repl_set_name", "auth_enabled", name="Replica / auth"),
    )

    class Meta:
        model = MongoDBConfig
        fields = ["server", "storage_engine", "cache_size_gb", "repl_set_name", "bind_ip",
                  "auth_enabled", "tags"]


class RedisConfigForm(NetBoxModelForm):
    server = DynamicModelChoiceField(queryset=DatabaseServer.objects.all())

    fieldsets = (
        FieldSet("server", "maxmemory", "maxmemory_policy", "databases", name="Redis / Valkey"),
        FieldSet("appendonly", "save_rule", "requirepass_ref", name="Persistence / auth"),
    )

    class Meta:
        model = RedisConfig
        fields = ["server", "maxmemory", "maxmemory_policy", "appendonly", "save_rule", "databases",
                  "requirepass_ref", "tags"]


class MosquittoConfigForm(NetBoxModelForm):
    server = DynamicModelChoiceField(queryset=DatabaseServer.objects.all())

    fieldsets = (
        FieldSet("server", "persistence", "max_connections", name="Mosquitto"),
        FieldSet("allow_anonymous", "password_file_ref", "tls_enabled", name="Auth / TLS"),
    )

    class Meta:
        model = MosquittoConfig
        fields = ["server", "persistence", "allow_anonymous", "max_connections", "password_file_ref",
                  "tls_enabled", "tags"]


class DatabaseForm(NetBoxModelForm):
    server = DynamicModelChoiceField(queryset=DatabaseServer.objects.all())

    fieldsets = (FieldSet("server", "name", "owner", "charset", "collation", name="Database"),)

    class Meta:
        model = Database
        fields = ["server", "name", "owner", "charset", "collation", "tags"]


class DatabaseUserForm(NetBoxModelForm):
    server = DynamicModelChoiceField(queryset=DatabaseServer.objects.all())

    fieldsets = (FieldSet("server", "username", "host_scope", "credential_ref", name="User"),)

    class Meta:
        model = DatabaseUser
        fields = ["server", "username", "host_scope", "credential_ref", "tags"]


class DatabaseGrantForm(NetBoxModelForm):
    user = DynamicModelChoiceField(queryset=DatabaseUser.objects.all())
    database = DynamicModelChoiceField(queryset=Database.objects.all())

    fieldsets = (FieldSet("user", "database", "privileges", name="Grant"),)

    class Meta:
        model = DatabaseGrant
        fields = ["user", "database", "privileges", "tags"]


class GaleraClusterForm(NetBoxModelForm):
    fieldsets = (FieldSet("name", "sst_method", "cluster_address", name="Galera cluster"),)

    class Meta:
        model = GaleraCluster
        fields = ["name", "sst_method", "cluster_address", "tags"]


class GaleraNodeForm(NetBoxModelForm):
    cluster = DynamicModelChoiceField(queryset=GaleraCluster.objects.all())
    server = DynamicModelChoiceField(queryset=DatabaseServer.objects.all())

    fieldsets = (FieldSet("cluster", "server", "node_address", "is_bootstrap", "segment", name="Galera node"),)

    class Meta:
        model = GaleraNode
        fields = ["cluster", "server", "node_address", "is_bootstrap", "segment", "tags"]


class PostgresClusterForm(NetBoxModelForm):
    fieldsets = (FieldSet("name", "ha_mode", "dcs_reference", "synchronous", name="Postgres cluster"),)

    class Meta:
        model = PostgresCluster
        fields = ["name", "ha_mode", "dcs_reference", "synchronous", "tags"]


class PostgresClusterNodeForm(NetBoxModelForm):
    cluster = DynamicModelChoiceField(queryset=PostgresCluster.objects.all())
    server = DynamicModelChoiceField(queryset=DatabaseServer.objects.all())

    fieldsets = (
        FieldSet("cluster", "server", "role", "replication_slot", "is_synchronous_standby", name="Postgres node"),
    )

    class Meta:
        model = PostgresClusterNode
        fields = ["cluster", "server", "role", "replication_slot", "is_synchronous_standby", "tags"]


class DatabaseServerFilterForm(NetBoxModelFilterSetForm):
    model = DatabaseServer
    engine = forms.MultipleChoiceField(choices=DatabaseEngineChoices, required=False)
    device_id = DynamicModelMultipleChoiceField(queryset=Device.objects.all(), required=False, label="Device")
    virtual_machine_id = DynamicModelMultipleChoiceField(queryset=VirtualMachine.objects.all(), required=False, label="VM")
    on_zfs = forms.NullBooleanField(required=False)
    tag = TagFilterField(DatabaseServer)


class MariaDBConfigFilterForm(NetBoxModelFilterSetForm):
    model = MariaDBConfig
    server_id = DynamicModelMultipleChoiceField(queryset=DatabaseServer.objects.all(), required=False, label="Server")
    tag = TagFilterField(MariaDBConfig)


class PostgresConfigFilterForm(NetBoxModelFilterSetForm):
    model = PostgresConfig
    server_id = DynamicModelMultipleChoiceField(queryset=DatabaseServer.objects.all(), required=False, label="Server")
    tag = TagFilterField(PostgresConfig)


class MongoDBConfigFilterForm(NetBoxModelFilterSetForm):
    model = MongoDBConfig
    server_id = DynamicModelMultipleChoiceField(queryset=DatabaseServer.objects.all(), required=False, label="Server")
    storage_engine = forms.MultipleChoiceField(choices=MongoStorageEngineChoices, required=False)
    auth_enabled = forms.NullBooleanField(required=False)
    tag = TagFilterField(MongoDBConfig)


class RedisConfigFilterForm(NetBoxModelFilterSetForm):
    model = RedisConfig
    server_id = DynamicModelMultipleChoiceField(queryset=DatabaseServer.objects.all(), required=False, label="Server")
    maxmemory_policy = forms.MultipleChoiceField(choices=RedisMaxmemoryPolicyChoices, required=False)
    appendonly = forms.NullBooleanField(required=False)
    tag = TagFilterField(RedisConfig)


class MosquittoConfigFilterForm(NetBoxModelFilterSetForm):
    model = MosquittoConfig
    server_id = DynamicModelMultipleChoiceField(queryset=DatabaseServer.objects.all(), required=False, label="Server")
    persistence = forms.MultipleChoiceField(choices=MosquittoPersistenceChoices, required=False)
    allow_anonymous = forms.NullBooleanField(required=False)
    tls_enabled = forms.NullBooleanField(required=False)
    tag = TagFilterField(MosquittoConfig)


class DatabaseFilterForm(NetBoxModelFilterSetForm):
    model = Database
    server_id = DynamicModelMultipleChoiceField(queryset=DatabaseServer.objects.all(), required=False, label="Server")
    tag = TagFilterField(Database)


class DatabaseUserFilterForm(NetBoxModelFilterSetForm):
    model = DatabaseUser
    server_id = DynamicModelMultipleChoiceField(queryset=DatabaseServer.objects.all(), required=False, label="Server")
    tag = TagFilterField(DatabaseUser)


class DatabaseGrantFilterForm(NetBoxModelFilterSetForm):
    model = DatabaseGrant
    user_id = DynamicModelMultipleChoiceField(queryset=DatabaseUser.objects.all(), required=False, label="User")
    database_id = DynamicModelMultipleChoiceField(queryset=Database.objects.all(), required=False, label="Database")
    tag = TagFilterField(DatabaseGrant)


class GaleraClusterFilterForm(NetBoxModelFilterSetForm):
    model = GaleraCluster
    sst_method = forms.MultipleChoiceField(choices=GaleraSSTMethodChoices, required=False)
    tag = TagFilterField(GaleraCluster)


class GaleraNodeFilterForm(NetBoxModelFilterSetForm):
    model = GaleraNode
    cluster_id = DynamicModelMultipleChoiceField(queryset=GaleraCluster.objects.all(), required=False, label="Cluster")
    server_id = DynamicModelMultipleChoiceField(queryset=DatabaseServer.objects.all(), required=False, label="Server")
    is_bootstrap = forms.NullBooleanField(required=False)
    tag = TagFilterField(GaleraNode)


class PostgresClusterFilterForm(NetBoxModelFilterSetForm):
    model = PostgresCluster
    ha_mode = forms.MultipleChoiceField(choices=PostgresHAModeChoices, required=False)
    synchronous = forms.NullBooleanField(required=False)
    tag = TagFilterField(PostgresCluster)


class PostgresClusterNodeFilterForm(NetBoxModelFilterSetForm):
    model = PostgresClusterNode
    cluster_id = DynamicModelMultipleChoiceField(queryset=PostgresCluster.objects.all(), required=False, label="Cluster")
    server_id = DynamicModelMultipleChoiceField(queryset=DatabaseServer.objects.all(), required=False, label="Server")
    role = forms.MultipleChoiceField(choices=PostgresRoleChoices, required=False)
    is_synchronous_standby = forms.NullBooleanField(required=False)
    tag = TagFilterField(PostgresClusterNode)
