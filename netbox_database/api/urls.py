# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.routers import NetBoxRouter
from . import views

app_name = "netbox_database"

router = NetBoxRouter()
router.register("servers", views.DatabaseServerViewSet)
router.register("mariadb-configs", views.MariaDBConfigViewSet)
router.register("postgres-configs", views.PostgresConfigViewSet)
router.register("mongodb-configs", views.MongoDBConfigViewSet)
router.register("redis-configs", views.RedisConfigViewSet)
router.register("mosquitto-configs", views.MosquittoConfigViewSet)
router.register("databases", views.DatabaseViewSet)
router.register("users", views.DatabaseUserViewSet)
router.register("grants", views.DatabaseGrantViewSet)
router.register("galera-clusters", views.GaleraClusterViewSet)
router.register("galera-nodes", views.GaleraNodeViewSet)
router.register("postgres-clusters", views.PostgresClusterViewSet)
router.register("postgres-cluster-nodes", views.PostgresClusterNodeViewSet)
router.register("mariadb-replications", views.MariaDBReplicationViewSet)
router.register("mariadb-replication-nodes", views.MariaDBReplicationNodeViewSet)

urlpatterns = router.urls
