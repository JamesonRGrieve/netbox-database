# SPDX-License-Identifier: AGPL-3.0-or-later
"""FilterSet tests against a real DB (no mocks): FK-id scoping, choice filters, and search()."""
from django.test import TestCase
from utilities.testing import create_test_device
from netbox_database.choices import (
    DatabaseEngineChoices, GaleraSSTMethodChoices, MariaDBReplicationRoleChoices,
    MariaDBReplicationSyncChoices, MariaDBReplicationTopologyChoices, MongoStorageEngineChoices,
    MosquittoPersistenceChoices, PostgresHAModeChoices, PostgresRoleChoices,
    RedisMaxmemoryPolicyChoices,
)
from netbox_database.filtersets import (
    DatabaseFilterSet, DatabaseGrantFilterSet, DatabaseServerFilterSet, DatabaseUserFilterSet,
    GaleraClusterFilterSet, GaleraNodeFilterSet, MariaDBReplicationFilterSet,
    MariaDBReplicationNodeFilterSet, MongoDBConfigFilterSet, MosquittoConfigFilterSet,
    PostgresClusterFilterSet, PostgresClusterNodeFilterSet, RedisConfigFilterSet,
)
from netbox_database.models import (
    Database, DatabaseGrant, DatabaseServer, DatabaseUser, GaleraCluster, GaleraNode,
    MariaDBReplication, MariaDBReplicationNode, MongoDBConfig, MosquittoConfig, PostgresCluster,
    PostgresClusterNode, RedisConfig,
)


def _server(name, engine=DatabaseEngineChoices.MARIADB, version="10.11", port=3306):
    return DatabaseServer.objects.create(
        name=name, engine=engine, version=version, port=port, device=create_test_device(f"h-{name}")
    )


class DatabaseServerFilterSetTest(TestCase):
    queryset = DatabaseServer.objects.all()

    @classmethod
    def setUpTestData(cls):
        cls.s1 = _server("mdb1", DatabaseEngineChoices.MARIADB)
        cls.s2 = _server("pg1", DatabaseEngineChoices.POSTGRESQL, "16", 5432)

    def test_engine(self):
        self.assertEqual(DatabaseServerFilterSet({"engine": ["postgresql"]}, self.queryset).qs.count(), 1)

    def test_device_id_scopes(self):
        self.assertEqual(DatabaseServerFilterSet({"device_id": [self.s1.device_id]}, self.queryset).qs.count(), 1)

    def test_search(self):
        self.assertEqual(DatabaseServerFilterSet({"q": "pg1"}, self.queryset).qs.count(), 1)


class DatabaseObjectsFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.s1 = _server("f1")
        cls.s2 = _server("f2")
        Database.objects.bulk_create([
            Database(server=cls.s1, name="alpha", owner="a"),
            Database(server=cls.s1, name="beta", owner="b"),
            Database(server=cls.s2, name="gamma", owner="c"),
        ])
        DatabaseUser.objects.bulk_create([
            DatabaseUser(server=cls.s1, username="ada"),
            DatabaseUser(server=cls.s1, username="bob"),
            DatabaseUser(server=cls.s2, username="cy"),
        ])

    def test_database_server_scope(self):
        self.assertEqual(DatabaseFilterSet({"server_id": [self.s1.pk]}, Database.objects.all()).qs.count(), 2)

    def test_database_search(self):
        self.assertEqual(DatabaseFilterSet({"q": "gamma"}, Database.objects.all()).qs.count(), 1)

    def test_user_server_scope(self):
        self.assertEqual(DatabaseUserFilterSet({"server_id": [self.s1.pk]}, DatabaseUser.objects.all()).qs.count(), 2)

    def test_user_search(self):
        self.assertEqual(DatabaseUserFilterSet({"q": "cy"}, DatabaseUser.objects.all()).qs.count(), 1)

    def test_grant_user_and_database_scope(self):
        u = DatabaseUser.objects.get(username="ada")
        d = Database.objects.get(name="alpha")
        DatabaseGrant.objects.create(user=u, database=d, privileges="ALL")
        qs = DatabaseGrant.objects.all()
        self.assertEqual(DatabaseGrantFilterSet({"user_id": [u.pk]}, qs).qs.count(), 1)
        self.assertEqual(DatabaseGrantFilterSet({"database_id": [d.pk]}, qs).qs.count(), 1)
        self.assertEqual(DatabaseGrantFilterSet({"q": "ALL"}, qs).qs.count(), 1)


class NonSqlConfigFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.mo1 = _server("mo1", DatabaseEngineChoices.MONGODB, "7.0", 27017)
        cls.mo2 = _server("mo2", DatabaseEngineChoices.MONGODB, "7.0", 27017)
        MongoDBConfig.objects.bulk_create([
            MongoDBConfig(server=cls.mo1, storage_engine=MongoStorageEngineChoices.WIREDTIGER, repl_set_name="rs0"),
            MongoDBConfig(server=cls.mo2, storage_engine=MongoStorageEngineChoices.INMEMORY),
        ])
        cls.re1 = _server("re1", DatabaseEngineChoices.REDIS, "7.2", 6379)
        cls.re2 = _server("re2", DatabaseEngineChoices.VALKEY, "8.0", 6379)
        RedisConfig.objects.bulk_create([
            RedisConfig(server=cls.re1, maxmemory="512mb", maxmemory_policy=RedisMaxmemoryPolicyChoices.ALLKEYS_LRU),
            RedisConfig(server=cls.re2, maxmemory_policy=RedisMaxmemoryPolicyChoices.NOEVICTION),
        ])
        cls.mq1 = _server("mq1", DatabaseEngineChoices.MOSQUITTO, "2.0", 1883)
        cls.mq2 = _server("mq2", DatabaseEngineChoices.MOSQUITTO, "2.0", 1883)
        MosquittoConfig.objects.bulk_create([
            MosquittoConfig(server=cls.mq1, persistence=MosquittoPersistenceChoices.FILE, tls_enabled=True),
            MosquittoConfig(server=cls.mq2, persistence=MosquittoPersistenceChoices.MEMORY),
        ])

    def test_mongodb_server_scope_engine_and_search(self):
        qs = MongoDBConfig.objects.all()
        self.assertEqual(MongoDBConfigFilterSet({"server_id": [self.mo1.pk]}, qs).qs.count(), 1)
        self.assertEqual(
            MongoDBConfigFilterSet({"storage_engine": [MongoStorageEngineChoices.INMEMORY]}, qs).qs.count(), 1
        )
        self.assertEqual(MongoDBConfigFilterSet({"q": "rs0"}, qs).qs.count(), 1)

    def test_redis_server_scope_policy_and_search(self):
        qs = RedisConfig.objects.all()
        self.assertEqual(RedisConfigFilterSet({"server_id": [self.re2.pk]}, qs).qs.count(), 1)
        self.assertEqual(
            RedisConfigFilterSet({"maxmemory_policy": [RedisMaxmemoryPolicyChoices.ALLKEYS_LRU]}, qs).qs.count(), 1
        )
        self.assertEqual(RedisConfigFilterSet({"q": "512mb"}, qs).qs.count(), 1)

    def test_mosquitto_server_scope_persistence_and_search(self):
        qs = MosquittoConfig.objects.all()
        self.assertEqual(MosquittoConfigFilterSet({"server_id": [self.mq1.pk]}, qs).qs.count(), 1)
        self.assertEqual(
            MosquittoConfigFilterSet({"persistence": [MosquittoPersistenceChoices.MEMORY]}, qs).qs.count(), 1
        )
        self.assertEqual(MosquittoConfigFilterSet({"q": "mq1"}, qs).qs.count(), 1)


class GaleraFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.c1 = GaleraCluster.objects.create(name="gcl-a", sst_method=GaleraSSTMethodChoices.MARIABACKUP)
        cls.c2 = GaleraCluster.objects.create(name="gcl-b", sst_method=GaleraSSTMethodChoices.RSYNC)
        cls.s1 = _server("gn1", DatabaseEngineChoices.MYSQL, "8.0")
        cls.s2 = _server("gn2", DatabaseEngineChoices.MARIADB)
        GaleraNode.objects.bulk_create([
            GaleraNode(cluster=cls.c1, server=cls.s1, node_address="10.0.0.1"),
            GaleraNode(cluster=cls.c1, server=cls.s2, node_address="10.0.0.2"),
        ])

    def test_cluster_sst_method(self):
        self.assertEqual(
            GaleraClusterFilterSet({"sst_method": [GaleraSSTMethodChoices.RSYNC]}, GaleraCluster.objects.all()).qs.count(), 1
        )

    def test_cluster_search(self):
        self.assertEqual(GaleraClusterFilterSet({"q": "gcl-b"}, GaleraCluster.objects.all()).qs.count(), 1)

    def test_node_cluster_scope_and_search(self):
        qs = GaleraNode.objects.all()
        self.assertEqual(GaleraNodeFilterSet({"cluster_id": [self.c1.pk]}, qs).qs.count(), 2)
        self.assertEqual(GaleraNodeFilterSet({"q": "10.0.0.1"}, qs).qs.count(), 1)


class PostgresClusterFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.c1 = PostgresCluster.objects.create(name="pcl-a", ha_mode=PostgresHAModeChoices.PATRONI)
        cls.c2 = PostgresCluster.objects.create(name="pcl-b", ha_mode=PostgresHAModeChoices.STREAMING)
        cls.s1 = _server("pn1", DatabaseEngineChoices.POSTGRESQL, "16", 5432)
        cls.s2 = _server("pn2", DatabaseEngineChoices.POSTGRESQL, "16", 5432)
        PostgresClusterNode.objects.bulk_create([
            PostgresClusterNode(cluster=cls.c1, server=cls.s1, role=PostgresRoleChoices.PRIMARY),
            PostgresClusterNode(cluster=cls.c1, server=cls.s2, role=PostgresRoleChoices.REPLICA),
        ])

    def test_cluster_ha_mode(self):
        self.assertEqual(
            PostgresClusterFilterSet({"ha_mode": [PostgresHAModeChoices.PATRONI]}, PostgresCluster.objects.all()).qs.count(), 1
        )

    def test_cluster_search(self):
        self.assertEqual(PostgresClusterFilterSet({"q": "pcl-b"}, PostgresCluster.objects.all()).qs.count(), 1)

    def test_node_cluster_scope_and_role(self):
        qs = PostgresClusterNode.objects.all()
        self.assertEqual(PostgresClusterNodeFilterSet({"cluster_id": [self.c1.pk]}, qs).qs.count(), 2)
        self.assertEqual(PostgresClusterNodeFilterSet({"role": [PostgresRoleChoices.PRIMARY]}, qs).qs.count(), 1)


class MariaDBReplicationFilterSetTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.r1 = MariaDBReplication.objects.create(
            name="mrepl-a", topology=MariaDBReplicationTopologyChoices.MASTER_MASTER,
            sync_mode=MariaDBReplicationSyncChoices.SEMI_SYNC,
        )
        cls.r2 = MariaDBReplication.objects.create(
            name="mrepl-b", topology=MariaDBReplicationTopologyChoices.MASTER_SLAVE,
        )
        cls.s1 = _server("mrn1", DatabaseEngineChoices.MARIADB)
        cls.s2 = _server("mrn2", DatabaseEngineChoices.MYSQL, "8.0")
        MariaDBReplicationNode.objects.bulk_create([
            MariaDBReplicationNode(replication=cls.r1, server=cls.s1, mariadb_server_id=1, role=MariaDBReplicationRoleChoices.CO_PRIMARY),
            MariaDBReplicationNode(replication=cls.r1, server=cls.s2, mariadb_server_id=2, role=MariaDBReplicationRoleChoices.CO_PRIMARY),
        ])

    def test_group_topology_and_sync(self):
        self.assertEqual(
            MariaDBReplicationFilterSet({"topology": [MariaDBReplicationTopologyChoices.MASTER_MASTER]}, MariaDBReplication.objects.all()).qs.count(), 1
        )
        self.assertEqual(
            MariaDBReplicationFilterSet({"sync_mode": [MariaDBReplicationSyncChoices.SEMI_SYNC]}, MariaDBReplication.objects.all()).qs.count(), 1
        )

    def test_group_search(self):
        self.assertEqual(MariaDBReplicationFilterSet({"q": "mrepl-b"}, MariaDBReplication.objects.all()).qs.count(), 1)

    def test_node_replication_scope_role_and_search(self):
        qs = MariaDBReplicationNode.objects.all()
        self.assertEqual(MariaDBReplicationNodeFilterSet({"replication_id": [self.r1.pk]}, qs).qs.count(), 2)
        self.assertEqual(MariaDBReplicationNodeFilterSet({"role": [MariaDBReplicationRoleChoices.CO_PRIMARY]}, qs).qs.count(), 2)
        self.assertEqual(MariaDBReplicationNodeFilterSet({"q": "mrn1"}, qs).qs.count(), 1)
