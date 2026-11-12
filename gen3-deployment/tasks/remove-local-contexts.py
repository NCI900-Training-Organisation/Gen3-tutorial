"""Remove only named local cluster config entries; never contact a cluster."""
import os
from pathlib import Path
import re
import sys
import tempfile

import yaml


def write_config(path, data):
    # Replace atomically with private permissions; do not leave credential backups.
    fd, temporary = tempfile.mkstemp(dir=path.parent)
    try:
        with os.fdopen(fd, 'w') as stream:
            yaml.safe_dump(data, stream, sort_keys=False)
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    print('updated', path)


def cleanup_kubernetes(path, matches):
    if not path.exists():
        return
    data = yaml.safe_load(path.read_text()) or {}
    original = yaml.safe_dump(data)
    removed_users = set()
    contexts = []
    for entry in data.get('contexts') or []:
        if matches(entry['context'].get('cluster', '')):
            removed_users.add(entry['context'].get('user'))
        else:
            contexts.append(entry)
    remaining_clusters = {entry['context'].get('cluster') for entry in contexts}
    remaining_users = {entry['context'].get('user') for entry in contexts}
    data['contexts'] = contexts
    data['clusters'] = [entry for entry in data.get('clusters') or []
                        if not matches(entry['name']) or entry['name'] in remaining_clusters]
    data['users'] = [entry for entry in data.get('users') or []
                     if entry['name'] not in removed_users or entry['name'] in remaining_users]
    if data.get('current-context') not in {entry['name'] for entry in contexts}:
        data['current-context'] = ''
    if yaml.safe_dump(data) != original:
        write_config(path, data)


def cleanup_talos(path, matches):
    if not path.exists():
        return
    data = yaml.safe_load(path.read_text()) or {}
    contexts = data.get('contexts') or {}
    removed = [name for name in contexts if matches(name)]
    if not removed:
        return
    data['contexts'] = {name: value for name, value in contexts.items() if name not in removed}
    if data.get('context') in removed:
        data['context'] = next(iter(data['contexts']), '')
    write_config(path, data)


def main():
    cluster, talos_path = sys.argv[1:]
    matches = re.compile(re.escape(cluster) + r'(?:-\d+)?').fullmatch
    paths = os.environ.get('KUBECONFIG') or str(Path.home() / '.kube/config')
    # Merged KUBECONFIG editing could affect references in other files: refuse it.
    config_paths = list(dict.fromkeys(p for p in paths.split(os.pathsep) if p))
    if len(config_paths) != 1:
        raise SystemExit('Set KUBECONFIG to a single file before context cleanup.')
    cleanup_kubernetes(Path(config_paths[0]).expanduser(), matches)
    cleanup_talos(Path(talos_path).expanduser(), matches)


if __name__ == '__main__':
    main()
