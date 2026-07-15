# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.api.viewsets import NetBoxModelViewSet
from .. import filtersets
from ..models import (
    Database, DatabaseGrant, DatabaseServer, DatabaseUser, GaleraCluster, GaleraNode,
    MariaDBConfig, MariaDBReplication, MariaDBReplicationNode, MongoDBConfig, MosquittoConfig,
    PostgresCluster, PostgresClusterNode,
    PostgresConfig, RedisConfig,
)
from .serializers import (
    DatabaseGrantSerializer, DatabaseSerializer, DatabaseServerSerializer, DatabaseUserSerializer,
    GaleraClusterSerializer, GaleraNodeSerializer, MariaDBConfigSerializer,
    MariaDBReplicationNodeSerializer, MariaDBReplicationSerializer, MongoDBConfigSerializer,
    MosquittoConfigSerializer, PostgresClusterNodeSerializer, PostgresClusterSerializer,
    PostgresConfigSerializer, RedisConfigSerializer,
)


class DatabaseServerViewSet(NetBoxModelViewSet):
    queryset = DatabaseServer.objects.prefetch_related("device", "virtual_machine", "service_instance", "tags")
    serializer_class = DatabaseServerSerializer
    filterset_class = filtersets.DatabaseServerFilterSet


class MariaDBConfigViewSet(NetBoxModelViewSet):
    queryset = MariaDBConfig.objects.prefetch_related("server", "tags")
    serializer_class = MariaDBConfigSerializer
    filterset_class = filtersets.MariaDBConfigFilterSet


class PostgresConfigViewSet(NetBoxModelViewSet):
    queryset = PostgresConfig.objects.prefetch_related("server", "tags")
    serializer_class = PostgresConfigSerializer
    filterset_class = filtersets.PostgresConfigFilterSet


class MongoDBConfigViewSet(NetBoxModelViewSet):
    queryset = MongoDBConfig.objects.prefetch_related("server", "tags")
    serializer_class = MongoDBConfigSerializer
    filterset_class = filtersets.MongoDBConfigFilterSet


class RedisConfigViewSet(NetBoxModelViewSet):
    queryset = RedisConfig.objects.prefetch_related("server", "tags")
    serializer_class = RedisConfigSerializer
    filterset_class = filtersets.RedisConfigFilterSet


class MosquittoConfigViewSet(NetBoxModelViewSet):
    queryset = MosquittoConfig.objects.prefetch_related("server", "tags")
    serializer_class = MosquittoConfigSerializer
    filterset_class = filtersets.MosquittoConfigFilterSet


class DatabaseViewSet(NetBoxModelViewSet):
    queryset = Database.objects.prefetch_related("server", "tags")
    serializer_class = DatabaseSerializer
    filterset_class = filtersets.DatabaseFilterSet


class DatabaseUserViewSet(NetBoxModelViewSet):
    queryset = DatabaseUser.objects.prefetch_related("server", "tags")
    serializer_class = DatabaseUserSerializer
    filterset_class = filtersets.DatabaseUserFilterSet


class DatabaseGrantViewSet(NetBoxModelViewSet):
    queryset = DatabaseGrant.objects.prefetch_related("user", "database", "tags")
    serializer_class = DatabaseGrantSerializer
    filterset_class = filtersets.DatabaseGrantFilterSet


class GaleraClusterViewSet(NetBoxModelViewSet):
    queryset = GaleraCluster.objects.prefetch_related("tags")
    serializer_class = GaleraClusterSerializer
    filterset_class = filtersets.GaleraClusterFilterSet


class GaleraNodeViewSet(NetBoxModelViewSet):
    queryset = GaleraNode.objects.prefetch_related("cluster", "server", "tags")
    serializer_class = GaleraNodeSerializer
    filterset_class = filtersets.GaleraNodeFilterSet


class PostgresClusterViewSet(NetBoxModelViewSet):
    queryset = PostgresCluster.objects.prefetch_related("tags")
    serializer_class = PostgresClusterSerializer
    filterset_class = filtersets.PostgresClusterFilterSet


class PostgresClusterNodeViewSet(NetBoxModelViewSet):
    queryset = PostgresClusterNode.objects.prefetch_related("cluster", "server", "tags")
    serializer_class = PostgresClusterNodeSerializer
    filterset_class = filtersets.PostgresClusterNodeFilterSet


class MariaDBReplicationViewSet(NetBoxModelViewSet):
    queryset = MariaDBReplication.objects.prefetch_related("tags")
    serializer_class = MariaDBReplicationSerializer
    filterset_class = filtersets.MariaDBReplicationFilterSet


class MariaDBReplicationNodeViewSet(NetBoxModelViewSet):
    queryset = MariaDBReplicationNode.objects.prefetch_related("replication", "server", "tags")
    serializer_class = MariaDBReplicationNodeSerializer
    filterset_class = filtersets.MariaDBReplicationNodeFilterSet
