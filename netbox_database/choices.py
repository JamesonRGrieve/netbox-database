# SPDX-License-Identifier: AGPL-3.0-or-later
"""Choice sets for the database server + HA models. Values match the on-host tokens verbatim
(engine package family, Galera SST method, Postgres HA orchestrator, Postgres replication role)."""
from utilities.choices import ChoiceSet


class DatabaseEngineChoices(ChoiceSet):
    """Data engine the server runs. ``mariadb``/``mysql`` share the MySQL wire protocol and the
    my.cnf surface (:class:`MariaDBConfig`); ``postgresql`` has its own (:class:`PostgresConfig`).
    The non-SQL engines each own a config surface too: ``mongodb`` (:class:`MongoDBConfig`),
    ``redis``/``valkey`` (:class:`RedisConfig`), ``mosquitto`` (:class:`MosquittoConfig`)."""
    MARIADB = "mariadb"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    MONGODB = "mongodb"
    REDIS = "redis"
    VALKEY = "valkey"
    MOSQUITTO = "mosquitto"
    CHOICES = [
        (MARIADB, "MariaDB", "blue"),
        (MYSQL, "MySQL", "orange"),
        (POSTGRESQL, "PostgreSQL", "indigo"),
        (MONGODB, "MongoDB", "green"),
        (REDIS, "Redis", "red"),
        (VALKEY, "Valkey", "teal"),
        (MOSQUITTO, "Mosquitto (MQTT)", "purple"),
    ]


class MongoStorageEngineChoices(ChoiceSet):
    """MongoDB storage engine — ``wiredTiger`` (default, on-disk) or ``inMemory``."""
    WIREDTIGER = "wiredTiger"
    INMEMORY = "inMemory"
    CHOICES = [
        (WIREDTIGER, "WiredTiger", "green"),
        (INMEMORY, "In-Memory", "orange"),
    ]


class RedisMaxmemoryPolicyChoices(ChoiceSet):
    """Redis/Valkey key-eviction policy applied when ``maxmemory`` is reached."""
    NOEVICTION = "noeviction"
    ALLKEYS_LRU = "allkeys-lru"
    ALLKEYS_LFU = "allkeys-lfu"
    VOLATILE_LRU = "volatile-lru"
    VOLATILE_TTL = "volatile-ttl"
    CHOICES = [
        (NOEVICTION, "noeviction", "gray"),
        (ALLKEYS_LRU, "allkeys-lru", "blue"),
        (ALLKEYS_LFU, "allkeys-lfu", "cyan"),
        (VOLATILE_LRU, "volatile-lru", "orange"),
        (VOLATILE_TTL, "volatile-ttl", "yellow"),
    ]


class MosquittoPersistenceChoices(ChoiceSet):
    """Mosquitto message persistence backing — ``file`` (durable) or ``memory``."""
    FILE = "file"
    MEMORY = "memory"
    CHOICES = [
        (FILE, "File", "green"),
        (MEMORY, "Memory", "orange"),
    ]


class GaleraSSTMethodChoices(ChoiceSet):
    """State Snapshot Transfer method a Galera cluster uses to seed a joining node."""
    MARIABACKUP = "mariabackup"
    RSYNC = "rsync"
    MYSQLDUMP = "mysqldump"
    CHOICES = [
        (MARIABACKUP, "mariabackup", "green"),
        (RSYNC, "rsync", "blue"),
        (MYSQLDUMP, "mysqldump", "orange"),
    ]


class PostgresHAModeChoices(ChoiceSet):
    """PostgreSQL high-availability orchestration mode a :class:`PostgresCluster` uses."""
    PATRONI = "patroni"
    REPMGR = "repmgr"
    STREAMING = "streaming"
    CHOICES = [
        (PATRONI, "Patroni", "green"),
        (REPMGR, "repmgr", "blue"),
        (STREAMING, "Streaming replication", "gray"),
    ]


class PostgresRoleChoices(ChoiceSet):
    """Replication role a PostgreSQL node holds within its cluster."""
    PRIMARY = "primary"
    REPLICA = "replica"
    WITNESS = "witness"
    CHOICES = [
        (PRIMARY, "Primary", "green"),
        (REPLICA, "Replica", "blue"),
        (WITNESS, "Witness", "gray"),
    ]


class MariaDBReplicationTopologyChoices(ChoiceSet):
    """MariaDB/MySQL binlog-replication topology a group runs — one-way ``master-slave`` or
    bidirectional ``master-master`` (each node a source for the other). This is the async/semi-sync
    binlog replication Galera (synchronous write-set) does not cover."""
    MASTER_SLAVE = "master-slave"
    MASTER_MASTER = "master-master"
    CHOICES = [
        (MASTER_SLAVE, "Master-Slave", "blue"),
        (MASTER_MASTER, "Master-Master", "green"),
    ]


class MariaDBReplicationSyncChoices(ChoiceSet):
    """Durability of a MariaDB replication group — ``async`` (default binlog) or ``semi-sync``
    (the primary waits for a replica to ack the event via ``rpl_semi_sync``)."""
    ASYNC = "async"
    SEMI_SYNC = "semi-sync"
    CHOICES = [
        (ASYNC, "Asynchronous", "gray"),
        (SEMI_SYNC, "Semi-synchronous", "green"),
    ]


class MariaDBReplicationRoleChoices(ChoiceSet):
    """Role a server holds in a MariaDB replication group. ``co-primary`` is a writable node in a
    master-master pair (source and replica at once); ``source``/``replica`` are the one-way roles."""
    SOURCE = "source"
    REPLICA = "replica"
    CO_PRIMARY = "co-primary"
    CHOICES = [
        (SOURCE, "Source", "green"),
        (REPLICA, "Replica", "blue"),
        (CO_PRIMARY, "Co-primary", "purple"),
    ]
