#!/usr/bin/python3

import datetime
import sys
from kubernetes import client, config

hours_to_mark_old = float(sys.argv[1])

config.load_incluster_config()

namespaces = [
    item.metadata.name for item in client.CoreV1Api().list_namespace().items
    if item.metadata.name.endswith("-tenant")
]

for ns in namespaces:
    print(f"namespace: {ns}")
    env_binds_snapshots = [
        env["spec"]["snapshot"] for env
        in client.CustomObjectsApi().list_namespaced_custom_object(
            group="appstudio.redhat.com",
            version="v1alpha1",
            namespace=ns,
            plural ="snapshotenvironmentbindings",
        )["items"]
    ]

    print(env_binds_snapshots)

    release_snapshots = [
        rel["spec"]["snapshot"] for rel
        in client.CustomObjectsApi().list_namespaced_custom_object(
            group="appstudio.redhat.com",
            version="v1alpha1",
            namespace=ns,
            plural ="releases",
        )["items"]
    ]

    print(release_snapshots)

    snapshots = [
        snapshot["metadata"]["name"] for snapshot
        in client.CustomObjectsApi().list_namespaced_custom_object(
            group="appstudio.redhat.com",
            version="v1alpha1",
            namespace=ns,
            plural ="snapshots",
        )["items"]
        if datetime.datetime.strptime(
            snapshot["metadata"]["creationTimestamp"], "%Y-%m-%dT%H:%M:%SZ"
        ) < datetime.datetime.utcnow() - datetime.timedelta(hours=hours_to_mark_old)
    ]

    print(snapshots)

    snapshots_to_delete = [
        snapshot for snapshot in snapshots if snapshot not in (
            env_binds_snapshots + release_snapshots
        )
    ]

    print(snapshots_to_delete)
