<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-database

A NetBox 4.6 plugin: the **native source of truth for database server instances** — which engine
(MariaDB / MySQL / PostgreSQL) at which version listens on which host and port, the server's tuned
`my.cnf` / `postgresql.conf` surface (including the ZFS-aware knobs), the logical databases /
users / grants living on it, and the HA topology (Galera for MariaDB; Patroni / repmgr / streaming
for PostgreSQL).

It is what the `tofu-mariadb` / `tofu-postgres` providers read to realize a server. It does **not**
own table schema — applications own that via their own migrations.

## Scope

- **In scope:** server instances, engine + version + listener, tuned config, logical
  databases/users/grants, and engine-native clustering.
- **Out of scope:** table/column DDL (apps own it), secret values (OpenBao owns them), and
  cross-service application HA fail-over pairing (that already lives in `netbox-services`
  `HAMirror` — reused, never duplicated).

## Composes netbox-services

A running database server is (optionally) a `netbox_services.ServiceInstance`. `DatabaseServer`
FKs it, so `PluginConfig.required_plugins = ["netbox_services"]` and the migration depends on
`netbox_services.0001_initial`. This plugin is the **database-native layer on top of**
`ServiceInstance` — it references, it does not re-model (the `netbox-ai` pattern).

## Model

- **DatabaseServer** — `name`, `engine`, `version`, `port`, `listen_address`, `data_dir`, `on_zfs`;
  host is exactly one of `device` (raw-OS) or `virtual_machine` (enforced in `clean()`); optional
  `service_instance` composition link.
  - **MariaDBConfig** (1:1) — nullable tuned `my.cnf` fields (NULL = engine default): buffer pool,
    max connections, charset/collation, and the ZFS COW knobs `innodb_doublewrite` /
    `innodb_flush_method`.
  - **PostgresConfig** (1:1) — nullable tuned `postgresql.conf` fields: shared buffers, cache/work
    mem, max connections, the ZFS COW WAL knobs `wal_init_zero` / `wal_recycle`, and
    `password_encryption` (default `scram-sha-256`).
- **Database** (FK server) — `name`, `owner`, `charset`, `collation`. Unique per `(server, name)`.
- **DatabaseUser** (FK server) — `username`, `host_scope`, `credential_ref` (**OpenBao path**).
  Unique per `(server, username, host_scope)`.
- **DatabaseGrant** (FK user + database) — `privileges`. Unique per `(user, database)`.
- **GaleraCluster** / **GaleraNode** — MariaDB/MySQL synchronous write-set clustering.
- **PostgresCluster** / **PostgresClusterNode** — PostgreSQL HA (Patroni / repmgr / streaming).

All models inherit `NetBoxModel` (custom fields, tags, change logging, GraphQL, REST API).

## Secret policy

A database password is **never** a field here. `DatabaseUser.credential_ref` is an **OpenBao path
reference** (the `netbox-services` convention). NetBox holds the structure; OpenBao holds the
secret.

## Install

```bash
uv pip install --python /opt/netbox/venv/bin/python netbox-database   # or: pip install -e .
# add "netbox_database" to PLUGINS in configuration.py (netbox_services must be enabled too)
python manage.py migrate netbox_database
python manage.py collectstatic --no-input
systemctl restart netbox netbox-rq
```

## Develop / test

Tests run against a **real NetBox test database** (no mocks) via NetBox's Django test framework.

```bash
python /opt/netbox/app/netbox/manage.py test netbox_database --keepdb -v2
```

## License

AGPL-3.0-or-later.
