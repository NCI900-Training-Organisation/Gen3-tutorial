#!/usr/bin/env python3
"""Add/repair only the requested local training account; preserve other users."""
import base64
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import uuid

credentials = dict(line.split('=', 1) for line in Path(sys.argv[1]).read_text().splitlines()
                   if '=' in line and not line.startswith('#'))
admin_password = credentials['LDAP_ADMIN_PASSWORD']
password = json.load(sys.stdin)['password']
if not password:
    raise SystemExit('Training password cannot be empty')
admin_dn = 'cn=admin,dc=gen3,dc=kind,dc=test'
user_dn = 'uid=training,ou=people,dc=gen3,dc=kind,dc=test'
group_dn = 'cn=gen3-users,ou=Groups,dc=gen3,dc=kind,dc=test'
changed = False


def ldap(tool, args, secret=admin_password, expected=(0,)):
    result = subprocess.run(['docker', 'exec', '-i', 'gen3-ldap', tool, '-x', '-H',
                             'ldap://localhost:389', '-D', admin_dn if tool != 'ldapwhoami' else user_dn,
                             '-y', '/dev/stdin', *args], input=secret, text=True, capture_output=True)
    if result.returncode not in expected:
        # Never include stdin or the Docker invocation in errors.
        raise RuntimeError(f'{tool} failed (LDAP exit code {result.returncode})')
    return result


def apply_ldif(text, tool='ldapmodify'):
    path = '/tmp/gen3-add-training-' + uuid.uuid4().hex + '.ldif'
    try:
        subprocess.run(['docker', 'exec', '-i', 'gen3-ldap', '/bin/sh', '-ec',
                        'umask 077; cat > "$1"', 'write-ldif', path],
                       input=text, text=True, check=True, capture_output=True)
        ldap(tool, ['-f', path])
    finally:
        subprocess.run(['docker', 'exec', 'gen3-ldap', 'rm', '-f', path], capture_output=True)


# Verify the existing directory/group before creating an account.
ldap('ldapsearch', ['-LLL', '-b', group_dn, '-s', 'base', '(objectClass=*)', 'dn'])
exists = ldap('ldapsearch', ['-LLL', '-b', user_dn, '-s', 'base', '(objectClass=*)', 'dn'], expected=(0, 32))
# A separate UID prevents collisions with the original mongoose account.
collision = ldap('ldapsearch', ['-LLL', '-b', 'ou=people,dc=gen3,dc=kind,dc=test',
                               '(&(uidNumber=10002)(!(uid=training)))', 'dn'])
if 'dn:' in collision.stdout:
    raise RuntimeError('uidNumber 10002 belongs to another account; no account was changed')

salt = os.urandom(16)
ssha = '{SSHA}' + base64.b64encode(hashlib.sha1(password.encode() + salt).digest() + salt).decode()
if exists.returncode == 32:
    apply_ldif(f'''dn: {user_dn}
objectClass: inetOrgPerson
objectClass: posixAccount
cn: training
sn: training
uid: training
uidNumber: 10002
gidNumber: 10001
homeDirectory: /home/training
gecos: training
mail: training@gen3.kind.test
userPassword: {ssha}
''', 'ldapadd')
    changed = True
else:
    bind = ldap('ldapwhoami', [], secret=password, expected=(0, 49))
    if bind.returncode == 49:
        # Explicitly requested credentials: reset only this training account.
        apply_ldif(f'dn: {user_dn}\nchangetype: modify\nreplace: userPassword\nuserPassword: {ssha}\n')
        changed = True
member = ldap('ldapsearch', ['-LLL', '-b', group_dn, '-s', 'base', '(memberUid=training)', 'dn'])
if 'dn:' not in member.stdout:
    apply_ldif(f'dn: {group_dn}\nchangetype: modify\nadd: memberUid\nmemberUid: training\n')
    changed = True
ldap('ldapwhoami', [], secret=password)
print(json.dumps({'changed': changed, 'username': 'training', 'group': 'gen3-users', 'bind_verified': True}))
