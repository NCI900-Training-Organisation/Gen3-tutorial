#!/usr/bin/env python3
"""Create a one-shot policy/ETL Job from the installed workload's pod spec."""

import copy
import hashlib
import json
import sys

request = json.load(sys.stdin)
kind = request["kind"]
if kind == "policy":
    spec = copy.deepcopy(request["deployment"]["spec"]["template"]["spec"])
    container = spec["containers"][0]
    for key in ["ports", "livenessProbe", "readinessProbe", "startupProbe"]:
        container.pop(key, None)
    container["name"] = "usersync"
    container["command"] = ["/bin/bash", "-ec"]
    container["args"] = [
        """python /var/www/fence/yaml_merge.py /var/www/fence/fence-config-public.yaml /var/www/fence/fence-config-secret.yaml /var/www/fence/fence-config.yaml
fence-create sync --arborist http://arborist-service --yaml /training/user.yaml"""
    ]
    container.setdefault("volumeMounts", []).append(
        {"name": "training-policy", "mountPath": "/training", "readOnly": True}
    )
    spec["volumes"].append(
        {
            "name": "training-policy",
            "configMap": {
                "name": "useryaml",
                "items": [{"key": "useryaml", "path": "user.yaml"}],
            },
        }
    )
    spec["containers"] = [container]
    spec.pop("initContainers", None)
    spec["restartPolicy"] = "Never"
    spec["automountServiceAccountToken"] = False
    digest = hashlib.sha256(
        (request["policy"] + request.get("run_id", "")).encode()
    ).hexdigest()[:12]
    name = "gen3-usersync-" + digest
    job = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {"name": name, "namespace": "gen3"},
        "spec": {
            "backoffLimit": 0,
            "activeDeadlineSeconds": 600,
            "template": {"spec": spec},
        },
    }
else:
    job = {
        "apiVersion": "batch/v1",
        "kind": "Job",
        "metadata": {
            "name": request["name"],
            "namespace": "gen3",
            "labels": {"gen3.training/task": "etl"},
        },
        "spec": copy.deepcopy(request["cronjob"]["spec"]["jobTemplate"]["spec"]),
    }
    job["spec"]["activeDeadlineSeconds"] = 1800
    if request.get("force", False):
        containers = job["spec"]["template"]["spec"]["containers"]
        tube = next(
            (container for container in containers if container["name"] == "tube"), None
        )
        if tube is None:
            raise ValueError("The ETL template has no tube container")
        env = tube.setdefault("env", [])
        forced = next(
            (variable for variable in env if variable["name"] == "ETL_FORCED"), None
        )
        if forced is None:
            env.append({"name": "ETL_FORCED", "value": "true"})
        else:
            forced["value"] = "true"
print(json.dumps(job))
