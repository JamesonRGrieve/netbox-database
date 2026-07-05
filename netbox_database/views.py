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
