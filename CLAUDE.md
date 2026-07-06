# netbox-database — Agent Operating Guide

Adapted from the sibling `../netbox-services` / `../netbox-system-services` plugins (same
engineering + test discipline), re-targeted to the **database server layer**.

`netbox-database` is an **AGPL-3.0** NetBox 4.6 plugin: the **native source of truth for database
server instances, their tuned config, and their HA topology** — which engine (MariaDB / MySQL /
PostgreSQL) at which version listens where, the `my.cnf` / `postgresql.conf` surface (incl. the
ZFS-aware knobs), the logical databases / users / grants on the server, and the engine-native
clustering (Galera; Patroni / repmgr / streaming). It is what the `tofu-mariadb` / `tofu-postgres`
providers read. It does **not** own table schema — apps own that via their own migrations. See
**DESIGN.md** for the full data model, the compose boundary, and verification owed.

**It composes `netbox-services`, it does not re-model it (the netbox-ai pattern):** a running
server is (optionally) a `netbox_services.ServiceInstance` — `DatabaseServer` **FKs** it, so
`required_plugins = ["netbox_services"]` and the migration depends on `netbox_services.0001_initial`.
Cross-service application HA pairing already lives in `netbox_services.HAMirror` and is **reused,
never duplicated** — this plugin models only the *database-native* clustering `HAMirror` cannot
express.

**Secret policy (load-bearing):** a database password is **never** a field here.
`DatabaseUser.credential_ref` is an **OpenBao path** reference (the netbox-services convention).
NetBox holds the structure; OpenBao holds the secret.

---

## Key Directives / Rules

### DO, ALWAYS:
- If functionality won't work without a parameter, make it a **required positional** parameter.
- Any time you modify a source file, ensure its accompanying test under `netbox_database/tests/`
  contains **comprehensive tests for the change WITHOUT MOCKS**, so `manage.py test
  netbox_database` discovers them, and update any `.md` in the same directory that references it.
- Write concise code (avoid obvious comments; one-liners where possible).
- Model tuned config as **nullable typed fields** — NULL = engine default, a value = explicit
  override (the netbox-zfs settable-field precedent). Never a JSON blob.
- **SPDX header on every source file**: `# SPDX-License-Identifier: AGPL-3.0-or-later`.

### DO NOT, EVER, UNDER ANY CIRCUMSTANCE:
- Make assumptions, or answer with "is likely", "probably", or "might be".
- Store a database password (or any secret value) in a model field. Only OpenBao path references.
- Model table/column schema — apps own DDL via their own migrations. This plugin owns the *server*.
- Duplicate `netbox_services.HAMirror` or the service catalog — FK / reference them.
- Use frame-local or thread-local state instead of passing data via parameters.
- Skip a failing test; keep a broken path as a fallback; or re-implement a function in a second
  location to bypass the original. No bandaid fixes.
- **Mock the database, the ORM, the NetBox API test client, or any integration path.** Tests run
  against a **real test database** with real `DatabaseServer` / core `dcim.Device` /
  `virtualization.VirtualMachine` / `netbox_services.ServiceInstance` rows.

### Python / Django Guidelines:
- Import children of `datetime`: `from datetime import date` — never `import datetime`.
- Package-relative imports inside `netbox_database` (`from .models import DatabaseServer`);
  core/sibling use the real path (`from dcim.models import Device`,
  `from netbox_services.api.serializers import ServiceInstanceSerializer`).
- FKs to core/sibling models in `models.py` use **string labels** (`"dcim.Device"`,
  `"virtualization.VirtualMachine"`, `"netbox_services.ServiceInstance"`) — never import them there.
- Models inherit `netbox.models.NetBoxModel` (custom fields, tags, journaling, GraphQL — free).

---

## Architecture (NetBox 4.6 plugin)

| File | Responsibility |
|------|----------------|
| `__init__.py` | `PluginConfig` — name `netbox_database`, `base_url='database'`, min/max 4.6, `required_plugins=["netbox_services"]` |
| `choices.py` | `ChoiceSet`s: `DatabaseEngineChoices` (SQL + mongodb/redis/valkey/mosquitto), `GaleraSSTMethodChoices`, `PostgresHAModeChoices`, `PostgresRoleChoices`, `MongoStorageEngineChoices`, `RedisMaxmemoryPolicyChoices`, `MosquittoPersistenceChoices` |
| `models.py` | the 13 models below (with `clean()` host/engine rules) |
| `migrations/0001_initial.py`, `migrations/0002_mongodb_redis_mosquitto_configs.py` | hand-authored (NetBox disables makemigrations in prod); verify with `makemigrations --check --dry-run`; 0001 deps: dcim, extras, virtualization, netbox_services; 0002 (MongoDB/Redis/Mosquitto configs) deps: netbox_database 0001 |
| `api/serializers.py`, `api/views.py`, `api/urls.py` | REST (`NetBoxModelViewSet`, `NetBoxRouter`) — the contract the providers + seeder read; nests dcim/virtualization/netbox_services serializers |
| `filtersets.py` | `NetBoxModelFilterSet` per model (explicit `<fk>_id` + `search()`) |
| `tables.py`, `forms.py`, `navigation.py`, `views.py`, `urls.py` | UI (generic NetBox views; `_routes()` helper; PluginMenu groups Servers / Databases / Users & Grants / HA Clusters) |
| `graphql/__init__.py` | placeholder (auto GraphQL via `NetBoxModel`) |

### Model — server + config + logical objects + HA
- **DatabaseServer**: `name`·`engine`·`version`·`port`·`listen_address`·`data_dir`·`on_zfs`; host
  is exactly one of `device`("dcim.Device") XOR `virtual_machine`("virtualization.VirtualMachine")
  (`clean()`); optional `service_instance`("netbox_services.ServiceInstance", SET_NULL).
  - **MariaDBConfig** (1:1): nullable `my.cnf` — buffer pool, max_connections, charset/collation,
    ZFS `innodb_doublewrite`/`innodb_flush_method`, bind_address.
  - **PostgresConfig** (1:1): nullable `postgresql.conf` — shared_buffers, caches/work mem,
    max_connections, ZFS `wal_init_zero`/`wal_recycle`, `password_encryption` (scram-sha-256),
    `listen_addresses`.
  - **MongoDBConfig** (1:1, `mongodb` `clean()`): `mongod.conf` — `storage_engine`
    (wiredTiger/inMemory), `cache_size_gb` (nullable), `repl_set_name`, `bind_ip`, `auth_enabled`.
  - **RedisConfig** (1:1, `redis`/`valkey` `clean()`): `redis.conf` — `maxmemory`,
    `maxmemory_policy`, `appendonly`, `save_rule`, `databases`, `requirepass_ref` (OpenBao path).
  - **MosquittoConfig** (1:1, `mosquitto` `clean()`): `mosquitto.conf` — `persistence`
    (file/memory), `allow_anonymous`, `max_connections` (-1 = unlimited), `password_file_ref`
    (OpenBao path), `tls_enabled`.
- **Database** (FK server): `name`·`owner`·`charset`·`collation`; unique `(server, name)`.
- **DatabaseUser** (FK server): `username`·`host_scope`·`credential_ref` (OpenBao path); unique
  `(server, username, host_scope)`.
- **DatabaseGrant** (FK user + database): `privileges`; unique `(user, database)`.
- **GaleraCluster** / **GaleraNode** (1:1 server, MySQL-family `clean()`): Galera write-set HA.
- **PostgresCluster** / **PostgresClusterNode** (1:1 server, PostgreSQL `clean()`): Postgres HA.

---

## Testing (NO MOCKS — real DB, NetBox test framework)

- Tests live in `netbox_database/tests/` (`test_models.py`, `test_api.py`, `test_filtersets.py`).
  Build real servers via a `make_server`/`_server` helper over `create_test_device` /
  `create_test_virtualmachine`. The per-server 1:1 rows (configs, cluster nodes) need a **fresh
  server per created object**; API `create_data` rows each target a fresh server/device.
- `test_models` covers `clean()` (host XOR, engine-family gates) + every uniqueness constraint +
  cascade; `test_api` runs the CRUD mixins per model; `test_filtersets` covers FK-id scoping,
  choice filters, and `search()`.
- **Run**: `python /opt/netbox/app/netbox/manage.py test netbox_database --keepdb -v2`.
- **Verification owed (cannot run offline — no NetBox env in the build host):**
  `makemigrations netbox_database --check --dry-run` on an ephemeral NetBox, and a full test run.
  Re-confirm against the pinned NetBox 4.6: the FK-target serialization (`dcim.device`,
  `virtualization.virtualmachine`, `netbox_services.serviceinstance`), the migration `dependencies`,
  and the `netbox_services.api.serializers.ServiceInstanceSerializer` import path. `py_compile`
  passes on every module today.
- **Never skip a failing test** — fix the root cause.

---

## Licensing
- **AGPL-3.0-or-later** (workspace production-IaC standard). SPDX header in every file.
