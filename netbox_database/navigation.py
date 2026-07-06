# SPDX-License-Identifier: AGPL-3.0-or-later
from netbox.plugins import PluginMenu, PluginMenuButton, PluginMenuItem


def _item(model, label):
    return PluginMenuItem(
        link=f"plugins:netbox_database:{model}_list",
        link_text=label,
        buttons=[
            PluginMenuButton(f"plugins:netbox_database:{model}_add", "Add", "mdi mdi-plus-thick")
        ],
    )


menu = PluginMenu(
    label="Database",
    groups=(
        (
            "Servers",
            (
                _item("databaseserver", "Database Servers"),
                _item("mariadbconfig", "MariaDB Configs"),
                _item("postgresconfig", "Postgres Configs"),
                _item("mongodbconfig", "MongoDB Configs"),
                _item("redisconfig", "Redis Configs"),
                _item("mosquittoconfig", "Mosquitto Configs"),
            ),
        ),
        ("Databases", (_item("database", "Databases"),)),
        (
            "Users & Grants",
            (_item("databaseuser", "Database Users"), _item("databasegrant", "Database Grants")),
        ),
        (
            "HA Clusters",
            (
                _item("galeracluster", "Galera Clusters"),
                _item("galeranode", "Galera Nodes"),
                _item("postgrescluster", "Postgres Clusters"),
                _item("postgresclusternode", "Postgres Cluster Nodes"),
            ),
        ),
    ),
    icon_class="mdi mdi-database",
)
