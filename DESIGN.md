<!-- SPDX-License-Identifier: AGPL-3.0-or-later -->
# netbox-database — Design

## 0. Purpose

NetBox is the native source of truth for **database server instances and their configuration** —
the data the `tofu-mariadb` / `tofu-postgres` providers read to stand up and reconcile a real
database server. Table schema is explicitly **not** modeled: applications own their own tables via
their own migrations. This plugin owns the *server*, not the *schema*.

Everything is a real typed column or a child row — no `config_context`, no CustomField data-blob
(the workspace's retired anti-pattern). The tuned config surface maps 1:1 to the managed
`99-ansible.cnf` / `postgresql.conf` the ansible database playbooks emit, so a reconciler reads
each knob back losslessly.

## 1. Model diagram

```
                        netbox_services.ServiceInstance   dcim.Device   virtualization.VirtualMachine
                                     ▲ (opt FK)                ▲ (XOR host FK) ▲
                                     │                         │              │
                              ┌──────┴─────────────────────────┴──────────────┴──┐
                              │                DatabaseServer                     │
                              │  name·engine·version·port·listen_address·         │
                              │  data_dir·on_zfs                                   │
                              └───┬───────────┬────────────┬───────────┬──────────┘
              1:1 mariadb_config  │           │ 1:1        │ FK        │ FK
                     ┌────────────┘           │ postgres_  │ databases │ users
                     ▼                        ▼ config     ▼           ▼
                MariaDBConfig          PostgresConfig    Database    DatabaseUser
                (nullable my.cnf)     (nullable pg.conf)   │            │
                                                           │ FK grants  │ FK grants
                                                           └────► DatabaseGrant ◄──┘
                                                                  (user × database)

   MariaDB/MySQL HA (write-set)                 PostgreSQL HA (Patroni/repmgr/streaming)
   GaleraCluster ──< GaleraNode 1:1─ Server     PostgresCluster ──< PostgresClusterNode 1:1─ Server
```

- **DatabaseServer** is the anchor. Host is exactly one of `dcim.Device` (raw-OS install) or
  `virtualization.VirtualMachine` (the common CT/VM case) — enforced by `clean()` (`bool(device)
  != bool(vm)`). `service_instance` is an *optional* composition link to the netbox-services
  instance that deployed it (`on_delete=SET_NULL` — deleting the instance record must not cascade
  away the server SoT).
- **MariaDBConfig / PostgresConfig** are per-server 1:1. Every tuned field is **nullable →
  NULL = let the engine default apply**, a value = explicit override (the netbox-zfs settable-field
  precedent). The ZFS-only knobs (`innodb_doublewrite`/`innodb_flush_method`;
  `wal_init_zero`/`wal_recycle`) are set only when `server.on_zfs` and are emitted into the managed
  config only on ZFS-backed data dirs — matching `install_mariadb_configure.yml` /
  `install_postgresql_configure.yml`.
- **Database / DatabaseUser / DatabaseGrant** are the logical objects, uniquely keyed per server.
- **GaleraNode / PostgresClusterNode** are 1:1 to a server (a server participates in at most one
  cluster of its kind) and `clean()`-gated to the correct engine family.

## 2. The compose-with-netbox-services boundary

`netbox-services` already owns two things this plugin must **reference, not duplicate**:

1. **The service catalog + instance layer.** A deployed database *is* a `ServiceInstance` (its
   catalog row carries `database_type`, health endpoint, resources, etc.). `DatabaseServer`
   **FKs** that instance rather than re-modeling deployment metadata. `required_plugins =
   ["netbox_services"]` + the migration dependency on `netbox_services.0001_initial` make the
   dependency hard and fail-fast — the `netbox-ai` pattern.

2. **`HAMirror` — cross-service, application-level fail-over pairing** (mirror ⇒ primary, same
   catalog type; the Semaphore HA reconciler reads `mirror.catalog.ha_strategy`, e.g.
   `mariadb_master_master`). That expresses *"this WordPress mirror fails over to that WordPress
   primary."* It is **not** duplicated here.

   What `HAMirror` **cannot** express is the *database-native clustering topology*: Galera
   write-set synchronous replication (SST method, per-node `wsrep_node_address`, segments,
   bootstrap election) and PostgreSQL streaming replication (primary/replica/witness roles,
   replication slots, synchronous standby set, the Patroni DCS). Those are engine-internal and
   live here as `GaleraCluster`/`GaleraNode` and `PostgresCluster`/`PostgresClusterNode`. The two
   are **complementary**: `HAMirror` is the app-tier fail-over relationship; the cluster models are
   the storage-tier replication mechanism.

## 3. HA topology

- **MariaDB/MySQL → Galera.** Multi-primary synchronous write-set replication. A `GaleraCluster`
  fixes the SST method (`mariabackup` default, or `rsync`/`mysqldump`) and the `gcomm://`
  `cluster_address`. Each member is a `GaleraNode` (1:1 to a MySQL-family `DatabaseServer`) with a
  `node_address`, an `is_bootstrap` flag (the node that starts the cluster), and a `segment`
  (WAN-optimized grouping). `clean()` rejects a non-MySQL-family server.
- **PostgreSQL → Patroni / repmgr / streaming.** A `PostgresCluster` picks the orchestration
  `ha_mode`, an optional `dcs_reference` (etcd/consul for Patroni), and a `synchronous` toggle.
  Each member is a `PostgresClusterNode` (1:1 to a PostgreSQL `DatabaseServer`) with a `role`
  (primary/replica/witness), an optional `replication_slot`, and an `is_synchronous_standby` flag.
  `clean()` rejects a non-PostgreSQL server.

## 4. Secret-ref policy

A database password is **never** a model field. `DatabaseUser.credential_ref` is an **OpenBao path
reference** — the `netbox-services` `community_ref` / `credential_ref` convention. NetBox holds the
structure (which user exists on which server with which host scope and grants); OpenBao holds the
secret value, resolved at apply time by the provider. State and change logs therefore never carry a
plaintext credential.

## 5. Consumer note (how the providers read this)

- **`tofu-mariadb` / `tofu-postgres` (in-house providers)** read `DatabaseServer` +
  `MariaDBConfig`/`PostgresConfig` as the SoT for **install + config + HA**: install the engine at
  `version`, render the managed config from the nullable knobs (NULL → omit → engine default), and
  wire the Galera / Postgres cluster from the node rows.
- **Logical DB/user/grant CRUD executes via composed community providers** — `cyrilgdn/postgresql`
  and `petoju/mysql` — driven from the `Database` / `DatabaseUser` / `DatabaseGrant` rows. The
  in-house providers own the *server* lifecycle; the community providers own the *object* lifecycle
  inside a running server. The password each community provider needs is fetched from OpenBao at
  `credential_ref`, never from NetBox.

## 6. Verification owed (cannot run offline — no NetBox env in the build host)

The full NetBox Django test run and `makemigrations netbox_database --check --dry-run` require a
live NetBox and are **owed**, not yet run here. `python -m py_compile` passes on every module.
Re-confirm against the pinned NetBox 4.6:

- the `DatabaseServer` FK targets serialize (`dcim.device`, `virtualization.virtualmachine`,
  `netbox_services.serviceinstance`) and the migration `dependencies` resolve;
- the `ServiceInstanceSerializer` import path (`netbox_services.api.serializers`) is stable;
- run `python /opt/netbox/app/netbox/manage.py test netbox_database --keepdb -v2` green.

Open deep-work items are tracked in `todo.json` (live migration verification, ansible `about.json`
backfill, the seeder).
