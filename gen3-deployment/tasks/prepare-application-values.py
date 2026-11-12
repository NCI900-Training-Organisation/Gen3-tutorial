#!/usr/bin/env python3
"""Build private Helm values from preserved local state; stdout is secret-bearing."""
import json
import secrets
import sys
from pathlib import Path
import yaml

state = Path(sys.argv[1])
base = yaml.safe_load(Path(sys.argv[2]).read_text())
private = state / 'application-credentials.json'
if private.is_symlink():
    raise RuntimeError('Refusing a symlink for application credentials')
if private.exists():
    credentials = json.loads(private.read_text())
else:
    credentials = {k: secrets.token_hex(24) for k in ['postgres_password', 'service_password', 'session_key']}
    credentials['indexd'] = {k: secrets.token_hex(24) for k in ['fence', 'sheepdog', 'ssj', 'gateway']}
    # Exclusive creation prevents concurrent runs from silently replacing credentials.
    with open(private, 'x', opener=lambda p, f: __import__('os').open(p, f, 0o600)) as stream:
        json.dump(credentials, stream)
private.chmod(0o600)
minio = dict(line.split('=', 1) for line in (state / 'minio.env').read_text().splitlines() if '=' in line and not line.startswith('#'))
base['global']['postgres']['master'].update(host='gen3-postgres', username='postgres', password=credentials['postgres_password'])
for service in ['arborist', 'fence', 'indexd', 'sheepdog', 'peregrine']:
    base[service]['postgres']['password'] = credentials['service_password']
base['indexd']['secrets'] = {'userdb': credentials['indexd']}
fence = base['fence']
fence['jwtKeys'] = {'jwt_private_key.pem': (state / 'fence-jwt-private-key.pem').read_text()}
config = fence['FENCE_CONFIG']
config['ENCRYPTION_KEY'] = credentials['session_key']
config['INDEXD_PASSWORD'] = credentials['indexd']['fence']
config['OPENID_CONNECT']['generic_oidc_idp']['client_secret'] = (state / 'gen3-oidc-client-secret').read_text().strip()
config['AWS_CREDENTIALS'] = {'CRED1': {'aws_access_key_id': minio['MINIO_ROOT_USER'], 'aws_secret_access_key': minio['MINIO_ROOT_PASSWORD']}}
# Also supply standard AWS credentials for libraries using boto's default chain.
fence.setdefault('secrets', {}).update(awsAccessKeyId=minio['MINIO_ROOT_USER'], awsSecretAccessKey=minio['MINIO_ROOT_PASSWORD'])
print(json.dumps({'values': base, 'credentials': credentials}))
