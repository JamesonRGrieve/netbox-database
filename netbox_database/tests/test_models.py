# SPDX-License-Identifier: AGPL-3.0-or-later
"""Model tests against a real DB (no mocks): creation, str, clean() rules, constraints, cascades.

Each 1:1-to-server row (MariaDBConfig / PostgresConfig / GaleraNode / PostgresClusterNode) needs a
fresh DatabaseServer per created object, so helpers mint distinct servers/devices."""
from django.core.exceptions import ValidationError
from django.db import transaction
from django.db.utils import IntegrityError
from django.test import TestCase
from utilities.testing import create_test_device, create_test_virtualmachine
from netbox_database.choices import (
    DatabaseEngineChoices, GaleraSSTMethodChoices, PostgresHAModeChoices, PostgresRoleChoices,
)
from netbox_database.models import (
    Database, DatabaseGrant, DatabaseServer, DatabaseUser, GaleraCluster, GaleraNode,
    MariaDBConfig, MongoDBConfig, MosquittoConfig, PostgresCluster, PostgresClusterNode,
    PostgresConfig, RedisConfig,
)


def make_server(name, engine=DatabaseEngineChoices.MARIADB, version="10.11", port=3306):
    return DatabaseServer.objects.create(
        name=name, engine=engine, version=version, port=port,
        device=create_test_device(f"host-{name}"),
    )


class DatabaseServerModelTest(TestCase):
    def test_create_str_url_and_engine_color(self):
        s = make_server("db1")
        self.assertEqual(str(s), "db1 (mariadb 10.11)")
        self.assertIn("/plugins/database/servers/", s.get_absolute_url())
        self.assertEqual(s.get_engine_color(), "blue")
        self.assertEqual(s.host, s.device)

    def test_name_unique(self):
        make_server("dup")
        with self.assertRaises(IntegrityError), transaction.atomic():
            DatabaseServer.objects.create(
                name="dup", engine=DatabaseEngineChoices.MYSQL, version="8.0", port=3306,
                device=create_test_device("host-dup2"),
            )

    def test_clean_requires_exactly_one_host_none(self):
        s = DatabaseServer(name="nohost", engine=DatabaseEngineChoices.MARIADB, version="10.11", port=3306)
        with self.assertRaises(ValidationError):
            s.clean()

    def test_clean_rejects_both_hosts(self):
        s = DatabaseServer(
            name="bothhost", engine=DatabaseEngineChoices.MARIADB, version="10.11", port=3306,
            device=create_test_device("host-both"), virtual_machine=create_test_virtualmachine("vm-both"),
        )
        with self.assertRaises(ValidationError):
            s.clean()

    def test_clean_accepts_vm_only(self):
        s = DatabaseServer(
            name="vmonly", engine=DatabaseEngineChoices.POSTGRESQL, version="16", port=5432,
            virtual_machine=create_test_virtualmachine("vm-only"),
        )
        s.clean()  # no raise
        s.save()
        self.assertEqual(s.host, s.virtual_machine)


class ConfigModelTest(TestCase):
    def test_mariadb_config_defaults_str_and_one_per_server(self):
        s = make_server("mdb")
        c = MariaDBConfig.objects.create(server=s)
        self.assertEqual(c.character_set_server, "utf8mb4")
        self.assertEqual(c.collation_server, "utf8mb4_unicode_ci")
        self.assertIsNone(c.innodb_doublewrite)  # NULL = engine default
        self.assertEqual(str(c), f"MariaDB config: {s}")
        self.assertIn("/plugins/database/mariadb-configs/", c.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            MariaDBConfig.objects.create(server=s)

    def test_postgres_config_defaults_str_and_one_per_server(self):
        s = make_server("pg", engine=DatabaseEngineChoices.POSTGRESQL, version="16", port=5432)
        c = PostgresConfig.objects.create(server=s, wal_recycle=False, shared_buffers="512MB")
        self.assertEqual(c.password_encryption, "scram-sha-256")
        self.assertEqual(c.listen_addresses, "*")
        self.assertFalse(c.wal_recycle)
        self.assertIsNone(c.wal_init_zero)
        self.assertEqual(str(c), f"Postgres config: {s}")
        self.assertIn("/plugins/database/postgres-configs/", c.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            PostgresConfig.objects.create(server=s)


class NonSqlConfigModelTest(TestCase):
    def test_mongodb_config_defaults_str_clean_and_one_per_server(self):
        s = make_server("mongo", engine=DatabaseEngineChoices.MONGODB, version="7.0", port=27017)
        c = MongoDBConfig.objects.create(server=s)
        self.assertEqual(c.storage_engine, "wiredTiger")
        self.assertEqual(c.get_storage_engine_color(), "green")
        self.assertEqual(c.bind_ip, "0.0.0.0")
        self.assertTrue(c.auth_enabled)
        self.assertIsNone(c.cache_size_gb)  # NULL = engine default
        c.clean()  # no raise — mongodb engine
        self.assertEqual(str(c), f"MongoDB config: {s}")
        self.assertIn("/plugins/database/mongodb-configs/", c.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            MongoDBConfig.objects.create(server=s)

    def test_mongodb_config_rejects_non_mongodb_server(self):
        s = make_server("mongo-bad")  # mariadb
        c = MongoDBConfig(server=s)
        with self.assertRaises(ValidationError):
            c.clean()

    def test_redis_config_defaults_str_clean_and_one_per_server(self):
        s = make_server("redis", engine=DatabaseEngineChoices.REDIS, version="7.2", port=6379)
        c = RedisConfig.objects.create(server=s)
        self.assertEqual(c.maxmemory_policy, "noeviction")
        self.assertEqual(c.get_maxmemory_policy_color(), "gray")
        self.assertEqual(c.databases, 16)
        self.assertFalse(c.appendonly)
        c.clean()  # no raise — redis engine
        self.assertEqual(str(c), f"Redis config: {s}")
        self.assertIn("/plugins/database/redis-configs/", c.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            RedisConfig.objects.create(server=s)

    def test_redis_config_accepts_valkey_server(self):
        s = make_server("valkey", engine=DatabaseEngineChoices.VALKEY, version="8.0", port=6379)
        c = RedisConfig(server=s, maxmemory="512mb")
        c.clean()  # no raise — valkey is redis-family

    def test_redis_config_rejects_non_redis_server(self):
        s = make_server("redis-bad", engine=DatabaseEngineChoices.POSTGRESQL, version="16", port=5432)
        c = RedisConfig(server=s)
        with self.assertRaises(ValidationError):
            c.clean()

    def test_mosquitto_config_defaults_str_clean_and_one_per_server(self):
        s = make_server("mqtt", engine=DatabaseEngineChoices.MOSQUITTO, version="2.0", port=1883)
        c = MosquittoConfig.objects.create(server=s)
        self.assertEqual(c.persistence, "file")
        self.assertEqual(c.get_persistence_color(), "green")
        self.assertEqual(c.max_connections, -1)
        self.assertFalse(c.allow_anonymous)
        self.assertFalse(c.tls_enabled)
        c.clean()  # no raise — mosquitto engine
        self.assertEqual(str(c), f"Mosquitto config: {s}")
        self.assertIn("/plugins/database/mosquitto-configs/", c.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            MosquittoConfig.objects.create(server=s)

    def test_mosquitto_config_rejects_non_mosquitto_server(self):
        s = make_server("mqtt-bad")  # mariadb
        c = MosquittoConfig(server=s)
        with self.assertRaises(ValidationError):
            c.clean()


class DatabaseObjectsModelTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.server = make_server("obj")

    def test_database_str_url_and_unique(self):
        d = Database.objects.create(server=self.server, name="app", owner="app")
        self.assertEqual(str(d), "obj: app")
        self.assertIn("/plugins/database/databases/", d.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            Database.objects.create(server=self.server, name="app")

    def test_same_name_different_server_allowed(self):
        Database.objects.create(server=self.server, name="shared")
        other = make_server("obj2")
        Database.objects.create(server=other, name="shared")
        self.assertEqual(Database.objects.filter(name="shared").count(), 2)

    def test_user_str_url_and_unique(self):
        u = DatabaseUser.objects.create(server=self.server, username="app", credential_ref="db/app")
        self.assertEqual(str(u), "obj: app@%")
        self.assertEqual(u.credential_ref, "db/app")  # a path, not the secret
        self.assertIn("/plugins/database/users/", u.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            DatabaseUser.objects.create(server=self.server, username="app", host_scope="%")

    def test_user_same_name_different_host_scope_allowed(self):
        DatabaseUser.objects.create(server=self.server, username="app2", host_scope="%")
        DatabaseUser.objects.create(server=self.server, username="app2", host_scope="10.0.0.0/8")
        self.assertEqual(DatabaseUser.objects.filter(username="app2").count(), 2)

    def test_grant_str_url_and_unique(self):
        u = DatabaseUser.objects.create(server=self.server, username="g")
        d = Database.objects.create(server=self.server, name="gdb")
        g = DatabaseGrant.objects.create(user=u, database=d, privileges="ALL")
        self.assertEqual(str(g), "g@gdb: ALL")
        self.assertIn("/plugins/database/grants/", g.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            DatabaseGrant.objects.create(user=u, database=d, privileges="SELECT")

    def test_database_cascade_on_server_delete(self):
        Database.objects.create(server=self.server, name="cascade")
        DatabaseUser.objects.create(server=self.server, username="cascade")
        self.server.delete()
        self.assertEqual(Database.objects.count(), 0)
        self.assertEqual(DatabaseUser.objects.count(), 0)


class GaleraModelTest(TestCase):
    def test_cluster_defaults_str_color_and_unique(self):
        c = GaleraCluster.objects.create(name="galera-a")
        self.assertEqual(c.sst_method, GaleraSSTMethodChoices.MARIABACKUP)
        self.assertEqual(str(c), "galera-a")
        self.assertEqual(c.get_sst_method_color(), "green")
        self.assertIn("/plugins/database/galera-clusters/", c.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            GaleraCluster.objects.create(name="galera-a")

    def test_node_on_mysql_family_str_and_url(self):
        c = GaleraCluster.objects.create(name="galera-b")
        s = make_server("gnode", engine=DatabaseEngineChoices.MYSQL, version="8.0")
        n = GaleraNode.objects.create(cluster=c, server=s, node_address="10.0.0.1", is_bootstrap=True)
        n.clean()  # no raise — mysql family
        self.assertEqual(str(n), "galera-b: gnode")
        self.assertIn("/plugins/database/galera-nodes/", n.get_absolute_url())

    def test_node_rejects_postgres_server(self):
        c = GaleraCluster.objects.create(name="galera-c")
        s = make_server("gpg", engine=DatabaseEngineChoices.POSTGRESQL, version="16", port=5432)
        n = GaleraNode(cluster=c, server=s, node_address="10.0.0.2")
        with self.assertRaises(ValidationError):
            n.clean()

    def test_node_one_per_server(self):
        c = GaleraCluster.objects.create(name="galera-d")
        s = make_server("gone")
        GaleraNode.objects.create(cluster=c, server=s, node_address="10.0.0.3")
        with self.assertRaises(IntegrityError), transaction.atomic():
            GaleraNode.objects.create(cluster=c, server=s, node_address="10.0.0.4")


class PostgresClusterModelTest(TestCase):
    def test_cluster_defaults_str_color_and_unique(self):
        c = PostgresCluster.objects.create(name="pg-a", ha_mode=PostgresHAModeChoices.PATRONI)
        self.assertFalse(c.synchronous)
        self.assertEqual(str(c), "pg-a")
        self.assertEqual(c.get_ha_mode_color(), "green")
        self.assertIn("/plugins/database/postgres-clusters/", c.get_absolute_url())
        with self.assertRaises(IntegrityError), transaction.atomic():
            PostgresCluster.objects.create(name="pg-a", ha_mode=PostgresHAModeChoices.REPMGR)

    def test_node_on_postgres_str_color_and_url(self):
        c = PostgresCluster.objects.create(name="pg-b", ha_mode=PostgresHAModeChoices.STREAMING)
        s = make_server("pgnode", engine=DatabaseEngineChoices.POSTGRESQL, version="16", port=5432)
        n = PostgresClusterNode.objects.create(cluster=c, server=s, role=PostgresRoleChoices.PRIMARY)
        n.clean()  # no raise
        self.assertEqual(str(n), "pg-b: pgnode (primary)")
        self.assertEqual(n.get_role_color(), "green")
        self.assertIn("/plugins/database/postgres-cluster-nodes/", n.get_absolute_url())

    def test_node_rejects_mariadb_server(self):
        c = PostgresCluster.objects.create(name="pg-c", ha_mode=PostgresHAModeChoices.PATRONI)
        s = make_server("pgm")  # mariadb
        n = PostgresClusterNode(cluster=c, server=s, role=PostgresRoleChoices.REPLICA)
        with self.assertRaises(ValidationError):
            n.clean()
