# SPDX-License-Identifier: AGPL-3.0-or-later
"""netbox-database: NetBox as the native source of truth for **database server instances** —
which engine (MariaDB/MySQL/PostgreSQL) at which version listens on which host/port, the server's
tuned my.cnf / postgresql.conf surface (including the ZFS-aware knobs), the logical databases /
users / grants living on it, and the HA topology (Galera for MariaDB; Patroni/repmgr/streaming for
PostgreSQL). It is what the ``tofu-mariadb`` / ``tofu-postgres`` providers read to realize a server;
it does **not** own table schema — apps own that via their own migrations.

**It composes ``netbox-services``, it does not re-model it (the netbox-ai pattern):** a running
database server is (optionally) a :class:`netbox_services.ServiceInstance`; ``DatabaseServer`` FKs
it, so ``required_plugins = ["netbox_services"]`` and the migration depends on
``netbox_services.0001_initial``. Cross-service HA fail-over pairing (mirror⇒primary) already lives
in ``netbox_services.HAMirror`` and is **reused, never duplicated** — this plugin models only the
*database-native* clustering (Galera write-set replication, Postgres streaming replication) that
``HAMirror`` cannot express.

**Secret policy (load-bearing):** a database password is **never** a field here. ``DatabaseUser``
carries a ``credential_ref`` — an OpenBao path reference (the ``netbox-services``
``community_ref`` / ``credential_ref`` convention) — the secret value stays in OpenBao.
"""
from netbox.plugins import PluginConfig

__version__ = "0.0.1"


class NetBoxDatabaseConfig(PluginConfig):
    name = "netbox_database"
    verbose_name = "NetBox Database"
    description = "Native SoT for database server instances, config, and HA (MariaDB/MySQL/PostgreSQL)"
    version = __version__
    author = "Jameson"
    base_url = "database"
    min_version = "4.6.0"
    max_version = "4.6.99"
    # DatabaseServer.service_instance FKs netbox_services.ServiceInstance and the migration depends
    # on netbox_services.0001_initial, so the dependency is hard and fails fast at startup.
    required_plugins = ["netbox_services"]


config = NetBoxDatabaseConfig
