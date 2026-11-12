#!/usr/bin/env python3
"""Poll safe Job/Pod state: rc 0 complete, 1 pending, 2 failed. No logs/secrets."""
import json
import subprocess
import sys


def evaluate(job, pods):
    status = job.get('status') or {}
    if status.get('succeeded', 0):
        return 0, {'state': 'complete'}
    if status.get('failed', 0) or any(c.get('type') == 'Failed' and c.get('status') == 'True' for c in status.get('conditions', [])):
        return 2, {'state': 'failed', 'reason': 'JobFailed'}
    for pod in pods:
        state = pod.get('status') or {}
        for container in (state.get('initContainerStatuses') or []) + (state.get('containerStatuses') or []):
            waiting = (container.get('state') or {}).get('waiting') or {}
            reason = waiting.get('reason', '')
            if reason in {'ErrImagePull', 'ImagePullBackOff', 'InvalidImageName', 'CreateContainerConfigError', 'CreateContainerError'}:
                return 2, {'state': 'failed', 'reason': reason, 'container': container['name'], 'pod': pod['metadata']['name']}
    return 1, {'state': 'running'}


def main():
    job_name = sys.argv[1]
    try:
        objects = []
        for args in [['job', job_name], ['pods', '-l', 'job-name=' + job_name]]:
            r = subprocess.run(['kubectl', '--request-timeout=10s', 'get', *args, '-n', 'gen3', '-o', 'json'],
                               capture_output=True, text=True, timeout=15)
            if r.returncode:
                print(json.dumps({'state': 'pending', 'reason': 'KubernetesReadFailed'}))
                return 1
            objects.append(json.loads(r.stdout))
        rc, result = evaluate(objects[0], objects[1].get('items') or [])
    except (subprocess.TimeoutExpired, json.JSONDecodeError):
        rc, result = 1, {'state': 'pending', 'reason': 'KubernetesReadFailed'}
    print(json.dumps(result))
    return rc


if __name__ == '__main__':
    sys.exit(main())
