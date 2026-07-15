# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.views import generic
from . import filtersets, forms, models, tables


class DatabaseServerView(generic.ObjectView):
    queryset = models.DatabaseServer.objects.all()


class DatabaseServerListView(generic.ObjectListView):
    queryset = models.DatabaseServer.objects.all()
    table = tables.DatabaseServerTable
    filterset = filtersets.DatabaseServerFilterSet
    filterset_form = forms.DatabaseServerFilterForm


class DatabaseServerEditView(generic.ObjectEditView):
    queryset = models.DatabaseServer.objects.all()
    form = forms.DatabaseServerForm


class DatabaseServerDeleteView(generic.ObjectDeleteView):
    queryset = models.DatabaseServer.objects.all()


class DatabaseServerBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DatabaseServer.objects.all()
    table = tables.DatabaseServerTable


class MariaDBConfigView(generic.ObjectView):
    queryset = models.MariaDBConfig.objects.all()


class MariaDBConfigListView(generic.ObjectListView):
    queryset = models.MariaDBConfig.objects.all()
    table = tables.MariaDBConfigTable
    filterset = filtersets.MariaDBConfigFilterSet
    filterset_form = forms.MariaDBConfigFilterForm


class MariaDBConfigEditView(generic.ObjectEditView):
    queryset = models.MariaDBConfig.objects.all()
    form = forms.MariaDBConfigForm


class MariaDBConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.MariaDBConfig.objects.all()


class MariaDBConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.MariaDBConfig.objects.all()
    table = tables.MariaDBConfigTable


class PostgresConfigView(generic.ObjectView):
    queryset = models.PostgresConfig.objects.all()


class PostgresConfigListView(generic.ObjectListView):
    queryset = models.PostgresConfig.objects.all()
    table = tables.PostgresConfigTable
    filterset = filtersets.PostgresConfigFilterSet
    filterset_form = forms.PostgresConfigFilterForm


class PostgresConfigEditView(generic.ObjectEditView):
    queryset = models.PostgresConfig.objects.all()
    form = forms.PostgresConfigForm


class PostgresConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.PostgresConfig.objects.all()


class PostgresConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.PostgresConfig.objects.all()
    table = tables.PostgresConfigTable


class MongoDBConfigView(generic.ObjectView):
    queryset = models.MongoDBConfig.objects.all()


class MongoDBConfigListView(generic.ObjectListView):
    queryset = models.MongoDBConfig.objects.all()
    table = tables.MongoDBConfigTable
    filterset = filtersets.MongoDBConfigFilterSet
    filterset_form = forms.MongoDBConfigFilterForm


class MongoDBConfigEditView(generic.ObjectEditView):
    queryset = models.MongoDBConfig.objects.all()
    form = forms.MongoDBConfigForm


class MongoDBConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.MongoDBConfig.objects.all()


class MongoDBConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.MongoDBConfig.objects.all()
    table = tables.MongoDBConfigTable


class RedisConfigView(generic.ObjectView):
    queryset = models.RedisConfig.objects.all()


class RedisConfigListView(generic.ObjectListView):
    queryset = models.RedisConfig.objects.all()
    table = tables.RedisConfigTable
    filterset = filtersets.RedisConfigFilterSet
    filterset_form = forms.RedisConfigFilterForm


class RedisConfigEditView(generic.ObjectEditView):
    queryset = models.RedisConfig.objects.all()
    form = forms.RedisConfigForm


class RedisConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.RedisConfig.objects.all()


class RedisConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.RedisConfig.objects.all()
    table = tables.RedisConfigTable


class MosquittoConfigView(generic.ObjectView):
    queryset = models.MosquittoConfig.objects.all()


class MosquittoConfigListView(generic.ObjectListView):
    queryset = models.MosquittoConfig.objects.all()
    table = tables.MosquittoConfigTable
    filterset = filtersets.MosquittoConfigFilterSet
    filterset_form = forms.MosquittoConfigFilterForm


class MosquittoConfigEditView(generic.ObjectEditView):
    queryset = models.MosquittoConfig.objects.all()
    form = forms.MosquittoConfigForm


class MosquittoConfigDeleteView(generic.ObjectDeleteView):
    queryset = models.MosquittoConfig.objects.all()


class MosquittoConfigBulkDeleteView(generic.BulkDeleteView):
    queryset = models.MosquittoConfig.objects.all()
    table = tables.MosquittoConfigTable


class DatabaseView(generic.ObjectView):
    queryset = models.Database.objects.all()


class DatabaseListView(generic.ObjectListView):
    queryset = models.Database.objects.all()
    table = tables.DatabaseTable
    filterset = filtersets.DatabaseFilterSet
    filterset_form = forms.DatabaseFilterForm


class DatabaseEditView(generic.ObjectEditView):
    queryset = models.Database.objects.all()
    form = forms.DatabaseForm


class DatabaseDeleteView(generic.ObjectDeleteView):
    queryset = models.Database.objects.all()


class DatabaseBulkDeleteView(generic.BulkDeleteView):
    queryset = models.Database.objects.all()
    table = tables.DatabaseTable


class DatabaseUserView(generic.ObjectView):
    queryset = models.DatabaseUser.objects.all()


class DatabaseUserListView(generic.ObjectListView):
    queryset = models.DatabaseUser.objects.all()
    table = tables.DatabaseUserTable
    filterset = filtersets.DatabaseUserFilterSet
    filterset_form = forms.DatabaseUserFilterForm


class DatabaseUserEditView(generic.ObjectEditView):
    queryset = models.DatabaseUser.objects.all()
    form = forms.DatabaseUserForm


class DatabaseUserDeleteView(generic.ObjectDeleteView):
    queryset = models.DatabaseUser.objects.all()


class DatabaseUserBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DatabaseUser.objects.all()
    table = tables.DatabaseUserTable


class DatabaseGrantView(generic.ObjectView):
    queryset = models.DatabaseGrant.objects.all()


class DatabaseGrantListView(generic.ObjectListView):
    queryset = models.DatabaseGrant.objects.all()
    table = tables.DatabaseGrantTable
    filterset = filtersets.DatabaseGrantFilterSet
    filterset_form = forms.DatabaseGrantFilterForm


class DatabaseGrantEditView(generic.ObjectEditView):
    queryset = models.DatabaseGrant.objects.all()
    form = forms.DatabaseGrantForm


class DatabaseGrantDeleteView(generic.ObjectDeleteView):
    queryset = models.DatabaseGrant.objects.all()


class DatabaseGrantBulkDeleteView(generic.BulkDeleteView):
    queryset = models.DatabaseGrant.objects.all()
    table = tables.DatabaseGrantTable


class GaleraClusterView(generic.ObjectView):
    queryset = models.GaleraCluster.objects.all()


class GaleraClusterListView(generic.ObjectListView):
    queryset = models.GaleraCluster.objects.all()
    table = tables.GaleraClusterTable
    filterset = filtersets.GaleraClusterFilterSet
    filterset_form = forms.GaleraClusterFilterForm


class GaleraClusterEditView(generic.ObjectEditView):
    queryset = models.GaleraCluster.objects.all()
    form = forms.GaleraClusterForm


class GaleraClusterDeleteView(generic.ObjectDeleteView):
    queryset = models.GaleraCluster.objects.all()


class GaleraClusterBulkDeleteView(generic.BulkDeleteView):
    queryset = models.GaleraCluster.objects.all()
    table = tables.GaleraClusterTable


class GaleraNodeView(generic.ObjectView):
    queryset = models.GaleraNode.objects.all()


class GaleraNodeListView(generic.ObjectListView):
    queryset = models.GaleraNode.objects.all()
    table = tables.GaleraNodeTable
    filterset = filtersets.GaleraNodeFilterSet
    filterset_form = forms.GaleraNodeFilterForm


class GaleraNodeEditView(generic.ObjectEditView):
    queryset = models.GaleraNode.objects.all()
    form = forms.GaleraNodeForm


class GaleraNodeDeleteView(generic.ObjectDeleteView):
    queryset = models.GaleraNode.objects.all()


class GaleraNodeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.GaleraNode.objects.all()
    table = tables.GaleraNodeTable


class PostgresClusterView(generic.ObjectView):
    queryset = models.PostgresCluster.objects.all()


class PostgresClusterListView(generic.ObjectListView):
    queryset = models.PostgresCluster.objects.all()
    table = tables.PostgresClusterTable
    filterset = filtersets.PostgresClusterFilterSet
    filterset_form = forms.PostgresClusterFilterForm


class PostgresClusterEditView(generic.ObjectEditView):
    queryset = models.PostgresCluster.objects.all()
    form = forms.PostgresClusterForm


class PostgresClusterDeleteView(generic.ObjectDeleteView):
    queryset = models.PostgresCluster.objects.all()


class PostgresClusterBulkDeleteView(generic.BulkDeleteView):
    queryset = models.PostgresCluster.objects.all()
    table = tables.PostgresClusterTable


class PostgresClusterNodeView(generic.ObjectView):
    queryset = models.PostgresClusterNode.objects.all()


class PostgresClusterNodeListView(generic.ObjectListView):
    queryset = models.PostgresClusterNode.objects.all()
    table = tables.PostgresClusterNodeTable
    filterset = filtersets.PostgresClusterNodeFilterSet
    filterset_form = forms.PostgresClusterNodeFilterForm


class PostgresClusterNodeEditView(generic.ObjectEditView):
    queryset = models.PostgresClusterNode.objects.all()
    form = forms.PostgresClusterNodeForm


class PostgresClusterNodeDeleteView(generic.ObjectDeleteView):
    queryset = models.PostgresClusterNode.objects.all()


class PostgresClusterNodeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.PostgresClusterNode.objects.all()
    table = tables.PostgresClusterNodeTable


class MariaDBReplicationView(generic.ObjectView):
    queryset = models.MariaDBReplication.objects.all()


class MariaDBReplicationListView(generic.ObjectListView):
    queryset = models.MariaDBReplication.objects.all()
    table = tables.MariaDBReplicationTable
    filterset = filtersets.MariaDBReplicationFilterSet
    filterset_form = forms.MariaDBReplicationFilterForm


class MariaDBReplicationEditView(generic.ObjectEditView):
    queryset = models.MariaDBReplication.objects.all()
    form = forms.MariaDBReplicationForm


class MariaDBReplicationDeleteView(generic.ObjectDeleteView):
    queryset = models.MariaDBReplication.objects.all()


class MariaDBReplicationBulkDeleteView(generic.BulkDeleteView):
    queryset = models.MariaDBReplication.objects.all()
    table = tables.MariaDBReplicationTable


class MariaDBReplicationNodeView(generic.ObjectView):
    queryset = models.MariaDBReplicationNode.objects.all()


class MariaDBReplicationNodeListView(generic.ObjectListView):
    queryset = models.MariaDBReplicationNode.objects.all()
    table = tables.MariaDBReplicationNodeTable
    filterset = filtersets.MariaDBReplicationNodeFilterSet
    filterset_form = forms.MariaDBReplicationNodeFilterForm


class MariaDBReplicationNodeEditView(generic.ObjectEditView):
    queryset = models.MariaDBReplicationNode.objects.all()
    form = forms.MariaDBReplicationNodeForm


class MariaDBReplicationNodeDeleteView(generic.ObjectDeleteView):
    queryset = models.MariaDBReplicationNode.objects.all()


class MariaDBReplicationNodeBulkDeleteView(generic.BulkDeleteView):
    queryset = models.MariaDBReplicationNode.objects.all()
    table = tables.MariaDBReplicationNodeTable
