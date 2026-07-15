# SPDX-License-Identifier: AGPL-3.0-or-later
"""REST API CRUD tests against a real DB + real API client (no mocks).

Composes the explicit CRUD mixins (no GraphQL type shipped yet). DatabaseServer requires exactly
one host (device XOR VM), so each create row supplies a device pk. The per-server 1:1 rows
(configs, cluster nodes) need a fresh server per created object.
"""
import unittest
from decimal import Decimal

from utilities.testing import APIViewTestCases, create_test_device
from netbox_database.choices import (
    DatabaseEngineChoices, PostgresHAModeChoices, PostgresRoleChoices,
)
from netbox_database.models import (
    Database, DatabaseGrant, DatabaseServer, DatabaseUser, GaleraCluster, GaleraNode,
    MariaDBConfig, MariaDBReplication, MariaDBReplicationNode, MongoDBConfig, MosquittoConfig,
    PostgresCluster, PostgresClusterNode, PostgresConfig, RedisConfig,
)


class _CRUD(
    APIViewTestCases.GetObjectViewTestCase,
    APIViewTestCases.ListObjectsViewTestCase,
    APIViewTestCases.CreateObjectViewTestCase,
    APIViewTestCases.UpdateObjectViewTestCase,
    APIViewTestCases.DeleteObjectViewTestCase,
):
    # Plugin API views register under the `plugins-api:<app_label>-api` namespace;
    # without this override the test base reverses `<app_label>-api:…` (no
    # `plugins-api` prefix) → NoReverseMatch. See utilities/testing/api.py.
    view_namespace = "plugins-api:netbox_database"

    @classmethod
    def setUpClass(cls):
        if cls is _CRUD:
            raise unittest.SkipTest("abstract API test base")
        super().setUpClass()


def _server(name, engine=DatabaseEngineChoices.MARIADB, version="10.11", port=3306):
    return DatabaseServer.objects.create(
        name=name, engine=engine, version=version, port=port, device=create_test_device(f"h-{name}")
    )


class DatabaseServerAPITest(_CRUD):
    model = DatabaseServer
    brief_fields = ["display", "engine", "id", "name", "url", "version"]
    bulk_update_data = {"listen_address": "127.0.0.1"}

    @classmethod
    def setUpTestData(cls):
        for i in range(3):
            _server(f"exist-{i}")
        devs = [create_test_device(f"new-{i}") for i in range(3)]
        cls.create_data = [
            {"name": "srv-a", "engine": "mariadb", "version": "10.11", "port": 3306, "device": devs[0].pk},
            {"name": "srv-b", "engine": "postgresql", "version": "16", "port": 5432, "device": devs[1].pk, "on_zfs": True},
            {"name": "srv-c", "engine": "mysql", "version": "8.0", "port": 3306, "device": devs[2].pk},
        ]


class MariaDBConfigAPITest(_CRUD):
    model = MariaDBConfig
    brief_fields = ["display", "id", "server", "url"]
    bulk_update_data = {"max_connections": 200}

    @classmethod
    def setUpTestData(cls):
        MariaDBConfig.objects.bulk_create([MariaDBConfig(server=_server(f"mc-{i}")) for i in range(3)])
        news = [_server(f"mc-new-{i}") for i in range(3)]
        cls.create_data = [
            {"server": news[0].pk, "innodb_buffer_pool_size": "256M", "max_connections": 151},
            {"server": news[1].pk, "innodb_doublewrite": False, "innodb_flush_method": "fsync"},
            {"server": news[2].pk, "character_set_server": "utf8mb4", "bind_address": "0.0.0.0"},
        ]


class PostgresConfigAPITest(_CRUD):
    model = PostgresConfig
    brief_fields = ["display", "id", "server", "url"]
    bulk_update_data = {"max_connections": 300}

    @classmethod
    def setUpTestData(cls):
        PostgresConfig.objects.bulk_create([
            PostgresConfig(server=_server(f"pc-{i}", DatabaseEngineChoices.POSTGRESQL, "16", 5432)) for i in range(3)
        ])
        news = [_server(f"pc-new-{i}", DatabaseEngineChoices.POSTGRESQL, "16", 5432) for i in range(3)]
        cls.create_data = [
            {"server": news[0].pk, "shared_buffers": "512MB", "max_connections": 100},
            {"server": news[1].pk, "wal_init_zero": False, "wal_recycle": False},
            {"server": news[2].pk, "password_encryption": "scram-sha-256", "listen_addresses": "*"},
        ]


class MongoDBConfigAPITest(_CRUD):
    model = MongoDBConfig
    brief_fields = ["display", "id", "server", "url"]
    bulk_update_data = {"auth_enabled": False}

    @classmethod
    def setUpTestData(cls):
        MongoDBConfig.objects.bulk_create([
            MongoDBConfig(server=_server(f"mo-{i}", DatabaseEngineChoices.MONGODB, "7.0", 27017)) for i in range(3)
        ])
        news = [_server(f"mo-new-{i}", DatabaseEngineChoices.MONGODB, "7.0", 27017) for i in range(3)]
        cls.create_data = [
            {"server": news[0].pk, "storage_engine": "wiredTiger", "cache_size_gb": Decimal("2.50")},
            {"server": news[1].pk, "storage_engine": "inMemory", "repl_set_name": "rs0"},
            {"server": news[2].pk, "bind_ip": "0.0.0.0", "auth_enabled": False},
        ]


class RedisConfigAPITest(_CRUD):
    model = RedisConfig
    brief_fields = ["display", "id", "server", "url"]
    bulk_update_data = {"databases": 8}

    @classmethod
    def setUpTestData(cls):
        RedisConfig.objects.bulk_create([
            RedisConfig(server=_server(f"re-{i}", DatabaseEngineChoices.REDIS, "7.2", 6379)) for i in range(3)
        ])
        news = [_server(f"re-new-{i}", DatabaseEngineChoices.VALKEY, "8.0", 6379) for i in range(3)]
        cls.create_data = [
            {"server": news[0].pk, "maxmemory": "512mb", "maxmemory_policy": "allkeys-lru"},
            {"server": news[1].pk, "appendonly": True, "save_rule": "900 1 300 10"},
            {"server": news[2].pk, "databases": 4, "requirepass_ref": "db/redis"},
        ]


class MosquittoConfigAPITest(_CRUD):
    model = MosquittoConfig
    brief_fields = ["display", "id", "server", "url"]
    bulk_update_data = {"tls_enabled": True}

    @classmethod
    def setUpTestData(cls):
        MosquittoConfig.objects.bulk_create([
            MosquittoConfig(server=_server(f"mq-{i}", DatabaseEngineChoices.MOSQUITTO, "2.0", 1883)) for i in range(3)
        ])
        news = [_server(f"mq-new-{i}", DatabaseEngineChoices.MOSQUITTO, "2.0", 1883) for i in range(3)]
        cls.create_data = [
            {"server": news[0].pk, "persistence": "file", "max_connections": 1000},
            {"server": news[1].pk, "persistence": "memory", "allow_anonymous": True},
            {"server": news[2].pk, "tls_enabled": True, "password_file_ref": "db/mqtt"},
        ]


class DatabaseAPITest(_CRUD):
    model = Database
    brief_fields = ["display", "id", "name", "server", "url"]
    bulk_update_data = {"charset": "utf8mb4"}

    @classmethod
    def setUpTestData(cls):
        srv = _server("db-host")
        Database.objects.bulk_create([
            Database(server=srv, name="a"), Database(server=srv, name="b"), Database(server=srv, name="c"),
        ])
        cls.create_data = [
            {"server": srv.pk, "name": "k1", "owner": "k1"},
            {"server": srv.pk, "name": "k2", "charset": "utf8mb4", "collation": "utf8mb4_unicode_ci"},
            {"server": srv.pk, "name": "k3"},
        ]


class DatabaseUserAPITest(_CRUD):
    model = DatabaseUser
    brief_fields = ["display", "id", "server", "url", "username"]
    bulk_update_data = {"credential_ref": "db/rotated"}

    @classmethod
    def setUpTestData(cls):
        srv = _server("user-host")
        DatabaseUser.objects.bulk_create([
            DatabaseUser(server=srv, username="u1"),
            DatabaseUser(server=srv, username="u2", host_scope="10.0.0.0/8"),
            DatabaseUser(server=srv, username="u3", credential_ref="db/u3"),
        ])
        cls.create_data = [
            {"server": srv.pk, "username": "k1", "host_scope": "%", "credential_ref": "db/k1"},
            {"server": srv.pk, "username": "k2", "host_scope": "localhost"},
            {"server": srv.pk, "username": "k3"},
        ]


class DatabaseGrantAPITest(_CRUD):
    model = DatabaseGrant
    brief_fields = ["database", "display", "id", "url", "user"]
    # "USAGE" — a privilege none of the seed grants (ALL/SELECT/INSERT) already has,
    # so every row actually changes (bulk-update asserts len(changes) == len(data)).
    bulk_update_data = {"privileges": "USAGE"}

    @classmethod
    def setUpTestData(cls):
        srv = _server("grant-host")
        users = [DatabaseUser.objects.create(server=srv, username=f"gu{i}") for i in range(6)]
        dbs = [Database.objects.create(server=srv, name=f"gd{i}") for i in range(6)]
        DatabaseGrant.objects.bulk_create([
            DatabaseGrant(user=users[0], database=dbs[0], privileges="ALL"),
            DatabaseGrant(user=users[1], database=dbs[1], privileges="SELECT"),
            DatabaseGrant(user=users[2], database=dbs[2], privileges="INSERT"),
        ])
        cls.create_data = [
            {"user": users[3].pk, "database": dbs[3].pk, "privileges": "ALL"},
            {"user": users[4].pk, "database": dbs[4].pk, "privileges": "SELECT,INSERT"},
            {"user": users[5].pk, "database": dbs[5].pk, "privileges": "ALL PRIVILEGES"},
        ]


class GaleraClusterAPITest(_CRUD):
    model = GaleraCluster
    brief_fields = ["display", "id", "name", "sst_method", "url"]
    bulk_update_data = {"cluster_address": "gcomm://10.0.0.1,10.0.0.2"}

    @classmethod
    def setUpTestData(cls):
        GaleraCluster.objects.bulk_create([
            GaleraCluster(name="gc-a"), GaleraCluster(name="gc-b", sst_method="rsync"), GaleraCluster(name="gc-c"),
        ])
        cls.create_data = [
            {"name": "gk1", "sst_method": "mariabackup"},
            {"name": "gk2", "sst_method": "rsync", "cluster_address": "gcomm://"},
            {"name": "gk3", "sst_method": "mysqldump"},
        ]


class GaleraNodeAPITest(_CRUD):
    model = GaleraNode
    brief_fields = ["cluster", "display", "id", "server", "url"]
    bulk_update_data = {"segment": 1}

    @classmethod
    def setUpTestData(cls):
        cluster = GaleraCluster.objects.create(name="gn-cluster")
        GaleraNode.objects.bulk_create([
            GaleraNode(cluster=cluster, server=_server(f"gn-{i}", DatabaseEngineChoices.MYSQL, "8.0"), node_address=f"10.1.0.{i}")
            for i in range(3)
        ])
        news = [_server(f"gn-new-{i}", DatabaseEngineChoices.MYSQL, "8.0") for i in range(3)]
        cls.create_data = [
            {"cluster": cluster.pk, "server": news[0].pk, "node_address": "10.2.0.1", "is_bootstrap": True},
            {"cluster": cluster.pk, "server": news[1].pk, "node_address": "10.2.0.2", "segment": 1},
            {"cluster": cluster.pk, "server": news[2].pk, "node_address": "10.2.0.3"},
        ]


class PostgresClusterAPITest(_CRUD):
    model = PostgresCluster
    brief_fields = ["display", "ha_mode", "id", "name", "url"]
    bulk_update_data = {"synchronous": True}

    @classmethod
    def setUpTestData(cls):
        PostgresCluster.objects.bulk_create([
            PostgresCluster(name="pc-a", ha_mode="patroni"),
            PostgresCluster(name="pc-b", ha_mode="repmgr"),
            PostgresCluster(name="pc-c", ha_mode="streaming"),
        ])
        cls.create_data = [
            {"name": "pk1", "ha_mode": "patroni", "dcs_reference": "etcd-1"},
            {"name": "pk2", "ha_mode": "repmgr", "synchronous": True},
            {"name": "pk3", "ha_mode": "streaming"},
        ]


class PostgresClusterNodeAPITest(_CRUD):
    model = PostgresClusterNode
    brief_fields = ["cluster", "display", "id", "role", "server", "url"]
    bulk_update_data = {"is_synchronous_standby": True}

    @classmethod
    def setUpTestData(cls):
        cluster = PostgresCluster.objects.create(name="pcn-cluster", ha_mode="patroni")
        PostgresClusterNode.objects.bulk_create([
            PostgresClusterNode(cluster=cluster, server=_server(f"pcn-{i}", DatabaseEngineChoices.POSTGRESQL, "16", 5432), role=PostgresRoleChoices.REPLICA)
            for i in range(3)
        ])
        news = [_server(f"pcn-new-{i}", DatabaseEngineChoices.POSTGRESQL, "16", 5432) for i in range(3)]
        cls.create_data = [
            {"cluster": cluster.pk, "server": news[0].pk, "role": "primary"},
            {"cluster": cluster.pk, "server": news[1].pk, "role": "replica", "replication_slot": "slot1"},
            {"cluster": cluster.pk, "server": news[2].pk, "role": "witness", "is_synchronous_standby": True},
        ]


class MariaDBReplicationAPITest(_CRUD):
    model = MariaDBReplication
    brief_fields = ["display", "id", "name", "topology", "url"]
    bulk_update_data = {"sync_mode": "semi-sync"}

    @classmethod
    def setUpTestData(cls):
        MariaDBReplication.objects.bulk_create([
            MariaDBReplication(name="mr-a", topology="master-master"),
            MariaDBReplication(name="mr-b", topology="master-slave", sync_mode="semi-sync"),
            MariaDBReplication(name="mr-c", topology="master-master"),
        ])
        cls.create_data = [
            {"name": "mk1", "topology": "master-master"},
            {"name": "mk2", "topology": "master-slave", "sync_mode": "semi-sync", "gtid": False},
            {"name": "mk3", "topology": "master-master", "ssl": True},
        ]


class MariaDBReplicationNodeAPITest(_CRUD):
    model = MariaDBReplicationNode
    brief_fields = ["display", "id", "replication", "role", "server", "url"]
    bulk_update_data = {"read_only": True}

    @classmethod
    def setUpTestData(cls):
        repl = MariaDBReplication.objects.create(name="mn-repl", topology="master-master")
        MariaDBReplicationNode.objects.bulk_create([
            MariaDBReplicationNode(replication=repl, server=_server(f"mn-{i}"), mariadb_server_id=i + 1, role="co-primary")
            for i in range(3)
        ])
        news = [_server(f"mn-new-{i}") for i in range(3)]
        cls.create_data = [
            {"replication": repl.pk, "server": news[0].pk, "mariadb_server_id": 11, "role": "co-primary"},
            {"replication": repl.pk, "server": news[1].pk, "mariadb_server_id": 12, "role": "replica", "read_only": True},
            {"replication": repl.pk, "server": news[2].pk, "mariadb_server_id": 13, "role": "source"},
        ]
