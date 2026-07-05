# SPDX-License-Identifier: AGPL-3.0-or-later
"""Choice sets for the database server + HA models. Values match the on-host tokens verbatim
(engine package family, Galera SST method, Postgres HA orchestrator, Postgres replication role)."""
from utilities.choices import ChoiceSet


class DatabaseEngineChoices(ChoiceSet):
    """Relational engine the server runs. ``mariadb``/``mysql`` share the MySQL wire protocol and
    the my.cnf surface (:class:`MariaDBConfig`); ``postgresql`` has its own (:class:`PostgresConfig`)."""
    MARIADB = "mariadb"
    MYSQL = "mysql"
    POSTGRESQL = "postgresql"
    CHOICES = [
        (MARIADB, "MariaDB", "blue"),
        (MYSQL, "MySQL", "orange"),
        (POSTGRESQL, "PostgreSQL", "indigo"),
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
