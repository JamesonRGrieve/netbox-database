# SPDX-License-Identifier: AGPL-3.0-or-later
from django.urls import path
from netbox.views.generic import ObjectChangeLogView, ObjectJournalView
from . import models, views


def _routes(slug, name, model, list_view, edit_view, detail_view, delete_view, bulk_delete_view):
    return [
        path(f"{slug}/", list_view.as_view(), name=f"{name}_list"),
        path(f"{slug}/add/", edit_view.as_view(), name=f"{name}_add"),
        path(f"{slug}/delete/", bulk_delete_view.as_view(), name=f"{name}_bulk_delete"),
        path(f"{slug}/<int:pk>/", detail_view.as_view(), name=name),
        path(f"{slug}/<int:pk>/edit/", edit_view.as_view(), name=f"{name}_edit"),
        path(f"{slug}/<int:pk>/delete/", delete_view.as_view(), name=f"{name}_delete"),
        path(f"{slug}/<int:pk>/changelog/", ObjectChangeLogView.as_view(), name=f"{name}_changelog", kwargs={"model": model}),
        path(f"{slug}/<int:pk>/journal/", ObjectJournalView.as_view(), name=f"{name}_journal", kwargs={"model": model}),
    ]


urlpatterns = [
    *_routes("servers", "databaseserver", models.DatabaseServer,
             views.DatabaseServerListView, views.DatabaseServerEditView, views.DatabaseServerView,
             views.DatabaseServerDeleteView, views.DatabaseServerBulkDeleteView),
    *_routes("mariadb-configs", "mariadbconfig", models.MariaDBConfig,
             views.MariaDBConfigListView, views.MariaDBConfigEditView, views.MariaDBConfigView,
             views.MariaDBConfigDeleteView, views.MariaDBConfigBulkDeleteView),
    *_routes("postgres-configs", "postgresconfig", models.PostgresConfig,
             views.PostgresConfigListView, views.PostgresConfigEditView, views.PostgresConfigView,
             views.PostgresConfigDeleteView, views.PostgresConfigBulkDeleteView),
    *_routes("databases", "database", models.Database,
             views.DatabaseListView, views.DatabaseEditView, views.DatabaseView,
             views.DatabaseDeleteView, views.DatabaseBulkDeleteView),
    *_routes("users", "databaseuser", models.DatabaseUser,
             views.DatabaseUserListView, views.DatabaseUserEditView, views.DatabaseUserView,
             views.DatabaseUserDeleteView, views.DatabaseUserBulkDeleteView),
    *_routes("grants", "databasegrant", models.DatabaseGrant,
             views.DatabaseGrantListView, views.DatabaseGrantEditView, views.DatabaseGrantView,
             views.DatabaseGrantDeleteView, views.DatabaseGrantBulkDeleteView),
    *_routes("galera-clusters", "galeracluster", models.GaleraCluster,
             views.GaleraClusterListView, views.GaleraClusterEditView, views.GaleraClusterView,
             views.GaleraClusterDeleteView, views.GaleraClusterBulkDeleteView),
    *_routes("galera-nodes", "galeranode", models.GaleraNode,
             views.GaleraNodeListView, views.GaleraNodeEditView, views.GaleraNodeView,
             views.GaleraNodeDeleteView, views.GaleraNodeBulkDeleteView),
    *_routes("postgres-clusters", "postgrescluster", models.PostgresCluster,
             views.PostgresClusterListView, views.PostgresClusterEditView, views.PostgresClusterView,
             views.PostgresClusterDeleteView, views.PostgresClusterBulkDeleteView),
    *_routes("postgres-cluster-nodes", "postgresclusternode", models.PostgresClusterNode,
             views.PostgresClusterNodeListView, views.PostgresClusterNodeEditView, views.PostgresClusterNodeView,
             views.PostgresClusterNodeDeleteView, views.PostgresClusterNodeBulkDeleteView),
]
