# Local Gen3 application

Run from the tutorial repository after `01-build-infrastructure.yaml` succeeds:

```bash
source "$HOME/.gen3-local-tools/bin/activate"
ansible-playbook gen3-deployment/02-deploy-gen3.yaml
```

This installs PostgreSQL, Elasticsearch, Arborist, Fence (including its download
service), Indexd, Sheepdog, Peregrine, Guppy, Portal and the reverse proxy directly
with Helm. It uses the existing Dex, LDAP, MinIO, HTTP ingress and local-path
storage. There is no Argo CD, GitLab dependency, monitoring or certificate setup.

The dictionary defaults to `sample-data-dict/output-json/bundled-schema.json`
relative to the tutorial repository. It is copied unchanged into a ConfigMap and
served inside Kubernetes; the source file is retained. Override its location with
`-e dictionary_file=/absolute/path/bundled-schema.json`. The exploration mapping
in `config/gen3-values.yaml` targets this dictionary's patient/blood/DNA/seqrun
links; changing dictionaries requires reviewing those mappings and portal fields.
A changed deployed dictionary is refused unless `allow_dictionary_update=true`
is deliberately supplied after planning schema/data migration.

Passwords and the Fence signing key are generated once under `~/.gen3-local/`,
with private file permissions, and reused. MinIO and Dex credentials are read from
the completed infrastructure setup. Do not commit that directory, Helm values or
API credentials. Existing PostgreSQL password mismatches fail instead of rotating
passwords. PostgreSQL and Elasticsearch use separate 5 GiB local-path volumes.
Local storage is tied to the one Talos node; deleting the node loses its data.

The infrastructure Dex callback is extended to Fence's generic OIDC callback;
the client ID stays `gen3` and its secret stays unchanged. Application URLs and
session cookies are configured for HTTP. If this hostname was previously used
with HTTPS, clear its browser HSTS/site state or use a fresh browser profile.
Plain HTTP and LDAP are for the isolated local exercise only.

## Check the application

```bash
kubectl get pods,pvc -n gen3
kubectl get jobs -n gen3
curl -f http://gen3.kind.test/user/_status
```

Open **http://gen3.kind.test** and choose the LDAP login. Use username **mongoose**
and password **mangoose**. This training account receives administrator access;
it is intentionally unsuitable as a production authorization policy.

The playbook verifies service readiness, Indexd service passwords, authorization
sync and portal/Fence HTTP responses. It does not claim browser login, API token
creation or actual file transfer have passed. Complete these acceptance checks:

1. Log in and create/download API credentials from the portal Profile page.
2. Exchange the API key for an access token and make an authenticated API call.
3. Create program `training` and project `demo`, then submit a valid metadata
   record using the supplied dictionary. No sample patient records are inserted
   by deployment automation.
4. Upload a small file through Gen3 using your credentials, retain its GUID, and
   download it through Gen3. Compare the downloaded file's checksum with the
   original. Register its dictionary-compliant file metadata as needed.
5. Refresh search as below and confirm submitted records appear in Exploration.

## Refresh exploration after submitting metadata

The first deployment creates **empty mapped bootstrap indices behind aliases**
for `training_patient`, `training_file` and `training_array-config`. This lets
Guppy start without waiting for a first data-bearing ETL run. Existing indices
and array-configuration documents are never replaced by bootstrap.

ETL reads metadata from PostgreSQL and replaces its search aliases with versioned
indices. It does not upload the file bytes; those remain in MinIO. The ETL
CronJob stays suspended so the laptop does not start background Spark runs.
Run it explicitly after metadata submission:

```bash
ansible-playbook gen3-deployment/03-refresh-search.yaml
```

This creates a bounded Job from the installed ETL template, refuses overlapping
active runs, waits for success and restarts Guppy to pick up changed mappings.
Failed Jobs remain for diagnosis. This path still requires a successful live
run with actual training metadata; empty bootstrap mappings are not proof of ETL
correctness. Spark/Hadoop heaps are reduced for small local datasets; ETL can
still consume substantial memory alongside the application.

## Diagnose and retry

```bash
kubectl get pods,jobs -n gen3
kubectl describe pod -n gen3 <pod-name>
kubectl logs -n gen3 <pod-name> -c <container-name> --tail=100
```

Inspect logs privately: application errors can include configuration or tokens.
Rerun the application playbook after fixing the cause. To retry a failed policy
Job deliberately, use `-e initialization_run_id=retry1`; completed policy Jobs
are otherwise reused. No playbook automatically deletes application data.

## Offline validation

```bash
ansible-playbook gen3-deployment/02-deploy-gen3.yaml --syntax-check
ansible-playbook gen3-deployment/03-refresh-search.yaml --syntax-check
python gen3-deployment/tests/validate-application.py
```

Offline validation uses synthetic credentials and renders the local chart. It
checks secret consistency, HTTP settings, policy, search names, resource mounts
and bounded ETL settings. It does not pull container images or deploy workloads.
