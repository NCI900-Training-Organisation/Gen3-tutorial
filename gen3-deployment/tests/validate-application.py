#!/usr/bin/env python3
"""Offline Helm contract checks. Uses synthetic credentials, never live state."""
import base64
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import yaml

root = Path(__file__).resolve().parents[1]
with tempfile.TemporaryDirectory(prefix='gen3-application-check-') as temporary:
    state = Path(temporary)
    (state / 'minio.env').write_text('MINIO_ROOT_USER=fixture-user\nMINIO_ROOT_PASSWORD=fixture-password\n')
    (state / 'gen3-oidc-client-secret').write_text('fixture-client-secret')
    (state / 'fence-jwt-private-key.pem').write_text('FIXTURE-NOT-A-REAL-KEY')
    args = [sys.executable, str(root / 'tasks/prepare-application-values.py'), str(state), str(root / 'config/gen3-values.yaml')]
    first = json.loads(subprocess.check_output(args, text=True))
    second = json.loads(subprocess.check_output(args, text=True))
    assert first == second, 'Rerun rotated credentials'
    assert (state / 'application-credentials.json').stat().st_mode & 0o777 == 0o600
    values = state / 'values.yaml'
    values.write_text(yaml.safe_dump(first['values']))
    rendered = subprocess.check_output(['helm', 'template', 'gen3', str(root / 'charts/gen3'), '-n', 'gen3', '-f', str(values)], text=True)
    resources = [r for r in yaml.safe_load_all(rendered) if r]
    by_id = {(r['kind'], r['metadata']['name']): r for r in resources}
    assert len(by_id) == len(resources), 'Duplicate Kubernetes resource'
    for r in resources:
        if r['kind'] == 'ConfigMap':
            assert all(isinstance(v, str) for v in (r.get('data') or {}).values()), r['metadata']['name']
            payload = json.dumps(r.get('data') or {})
            assert len(payload.encode()) < 1048576, r['metadata']['name']
            for private_value in ['fixture-password', 'fixture-client-secret', first['credentials']['service_password'], first['credentials']['postgres_password']]:
                assert private_value not in payload, ('Private value leaked into ConfigMap', r['metadata']['name'])
        if r['kind'] == 'Secret':
            assert r.get('type') != 'kubernetes.io/tls'
        if r['kind'] == 'Deployment':
            spec = r['spec']['template']['spec']
            volumes = {v['name'] for v in (spec.get('volumes') or [])}
            for c in spec['containers'] + (spec.get('initContainers') or []):
                for m in c.get('volumeMounts', []):
                    assert m['name'] in volumes, (r['metadata']['name'], m['name'])
    for service in ['arborist', 'fence', 'indexd', 'sheepdog', 'peregrine']:
        secret = by_id['Secret', service + '-dbcreds']['data']
        assert base64.b64decode(secret['dbcreated']).strip() == b'true'
        assert base64.b64decode(secret['password']).decode() == first['credentials']['service_password']
        assert base64.b64decode(secret['host']).decode() == 'gen3-postgres'
    assert by_id['ConfigMap', 'manifest-global']['data']['cookie_domain'] == 'gen3.kind.test'
    fence = yaml.safe_load(by_id['Secret', 'fence-config']['stringData']['fence-config.yaml'])
    assert fence['SESSION_COOKIE_SECURE'] is False
    assert fence['BASE_URL'] == 'http://gen3.kind.test/user'
    assert fence['OPENID_CONNECT']['generic_oidc_idp']['client_id'] == 'gen3'
    assert fence['AWS_CREDENTIALS']['CRED1']['aws_secret_access_key'] == 'fixture-password'
    policy = yaml.safe_load(by_id['ConfigMap', 'useryaml']['data']['useryaml'])
    assert 'mongoose' in policy['users'] and 'mangoose' not in policy['users']
    def resource_paths(nodes, parent=''):
        paths = set()
        for node in nodes:
            path = parent + '/' + node['name']
            paths.add(path)
            paths.update(resource_paths(node.get('subresources', []), path))
        return paths
    declared = resource_paths(policy['authz']['resources'])
    for entry in policy['authz']['policies']:
        assert set(entry['resource_paths']) <= declared, ('Undefined authorization resource', entry['id'])

    nginx = by_id['ConfigMap', 'revproxy-nginx-conf']['data']['nginx.conf']
    assert 'return 301 https://' not in nginx and ';Secure;' not in nginx
    assert 'add_header "Strict-Transport-Security"' not in nginx
    guppy = json.loads(by_id['ConfigMap', 'manifest-guppy']['data']['guppy_config.json'])
    assert {i['index'] for i in guppy['indices']} == {'training_patient', 'training_file'}
    assert by_id['CronJob', 'etl-cronjob']['spec']['suspend'] is True
    portal = by_id['Deployment', 'portal-deployment']['spec']['template']['spec']['containers'][0]
    assert portal['resources']['limits']['memory'] == '3Gi'
    portal_spec = by_id['Deployment', 'portal-deployment']['spec']
    assert portal_spec['strategy']['type'] == 'Recreate'
    build = next(c for c in portal_spec['template']['spec']['initContainers'] if c['name'] == 'prepare-local-webpack')
    assert 'module.exports.devtool = false' in build['args'][0]
    assert 'module.exports.parallelism = 1' in build['args'][0]

    assert next(e['value'] for e in portal['env'] if e['name'] == 'NODE_OPTIONS') == '--max-old-space-size=1536'

    pod = by_id['CronJob', 'etl-cronjob']['spec']['jobTemplate']['spec']['template']['spec']
    assert all(e.get('value') != '8g' for c in pod['containers'] for e in c.get('env', []))
    tube = next(c for c in pod['containers'] if c['name'] == 'tube')
    assert tube['image'].endswith('@sha256:809c8451a2230976965fb3592f9c6ce1f5d70a23955a9da2fdef16b73610303d')

    # Exercise the actual policy Job builder against the rendered Fence deployment.
    job = json.loads(subprocess.check_output([sys.executable, str(root / 'tasks/make-initialization-job.py')],
        input=json.dumps({'kind': 'policy', 'deployment': by_id['Deployment', 'fence-deployment'],
                         'policy': json.dumps(policy), 'run_id': ''}), text=True))
    assert job['spec']['activeDeadlineSeconds'] == 600
    assert 'initContainers' not in job['spec']['template']['spec']
    assert 'fence-create sync' in job['spec']['template']['spec']['containers'][0]['args'][0]
    print(f'Passed runtime credential, HTTP, database, policy, search and ETL checks ({len(resources)} rendered resources).')
