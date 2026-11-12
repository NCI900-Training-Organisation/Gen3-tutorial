#!/usr/bin/env python3
"""Extend the active policy without removing accounts or unrelated resources."""
import copy
import json
import sys


def extend(source, active):
    result = copy.deepcopy(source)
    policy = copy.deepcopy(active)
    original = policy.get('users', {}).get('mongoose')
    if not isinstance(original, dict):
        raise ValueError('The mongoose policy template is missing; refusing to invent privileges')
    user = policy.setdefault('users', {}).setdefault('training', copy.deepcopy(original))
    user.setdefault('tags', {}).update(name='training', email='training@gen3.kind.test')
    for group in policy.get('authz', {}).get('groups', []):
        members = group.get('users', [])
        if 'mongoose' in members and 'training' not in members:
            members.append('training')
    import yaml
    result['fence']['USER_YAML'] = yaml.safe_dump(policy, sort_keys=False)
    return {'source_values': result, 'policy': policy}


if __name__ == '__main__':
    request = json.load(sys.stdin)
    print(json.dumps(extend(request['source_values'], request['active_policy'])))
