"""Create empty Guppy mappings/aliases only if absent. Never replace user data.

Run inside the dictionary pod. ETL later moves aliases to its own versioned
indices. Existing live indices and array-config documents remain authoritative.
"""
import json
from urllib.request import Request, urlopen
from urllib.error import HTTPError

HOST = 'http://gen3-elasticsearch:9200'

def call(method, path, body=None):
    request = Request(HOST + path, method=method,
        data=None if body is None else json.dumps(body).encode(),
        headers={'Content-Type': 'application/json'})
    try:
        with urlopen(request, timeout=30) as response:
            return response.status, json.loads(response.read() or b'{}')
    except HTTPError as error:
        if error.code == 404:
            return 404, {}
        raise

patient_fields = ['submitter_id', 'project_id', 'patient_id', '_patient_id', 'auth_resource_path']
file_fields = ['object_id', 'md5sum', 'file_name', 'data_category', 'data_format', 'data_type', 'state', 'seqrun_id', 'dna_id', '_patient_id', 'project_id', 'auth_resource_path']
indices = {
    'training_patient': {**{name: {'type': 'keyword'} for name in patient_fields},
        **{name: {'type': 'long'} for name in ['_blood_count', '_urine_count', '_dna_count', '_seqrun_count']}},
    'training_file': {**{name: {'type': 'keyword'} for name in file_fields}, 'file_size': {'type': 'long'}},
}
for alias, fields in indices.items():
    if call('HEAD', '/' + alias)[0] == 404:
        physical = alias + '_bootstrap_v1'
        # A failed previous PUT can be resumed; do not delete or rewrite mappings.
        if call('HEAD', '/' + physical)[0] == 404:
            call('PUT', '/' + physical, {'settings': {'number_of_shards': 1, 'number_of_replicas': 0},
                'mappings': {'properties': fields}})
        call('POST', '/_aliases', {'actions': [{'add': {'index': physical, 'alias': alias}}]})
    existing = call('GET', '/' + alias + '/_mapping')[1]
    assert existing and all('properties' in item.get('mappings', {}) for item in existing.values()), alias
config = 'training_array-config'
if call('HEAD', '/' + config)[0] == 404:
    call('PUT', '/' + config + '_bootstrap_v1', {'aliases': {config: {}}, 'settings': {'number_of_shards': 1, 'number_of_replicas': 0},
        'mappings': {'properties': {'array': {'type': 'keyword'}}}})
for name in indices:
    path = '/' + config + '/_doc/' + name
    if call('GET', path)[0] == 404:
        arrays = ['auth_resource_path'] + (['_patient_id'] if name.endswith('_file') else [])
        call('PUT', path + '?refresh=true', {'array': arrays})
print('Patient/file aliases and array configuration are ready; existing data retained.')
