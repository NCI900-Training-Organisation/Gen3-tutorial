# Local Gen3 chart

Vendored from the existing Gen3 0.3.103 chart in gen3-deploy. Only arborist,
fence, indexd, sheepdog, peregrine, portal, revproxy, guppy, etl and common are retained.
Application images use the 2025.08 release series; chart and images have separate
versions. The common dbcreated flag patch is retained for external DB bootstrap.

Local HTTP patches remove the revproxy certificate template, forced redirects,
HSTS and Secure cookie flags, and change Sheepdog/Peregrine Fence issuers to HTTP.
Fence BASE_URL comes exclusively from values. Ansible owns Indexd-user and policy
initialization instead of chart Jobs/Argo hooks. No TLS verification bypasses are
introduced for internet connections. Original source in gen3-deploy is unchanged.

ETL is manual and suspended by default; Spark driver/executor heaps are 512m,
Hadoop client heap is 256m and daemon heaps are bounded for laptop use. Search
bootstrap creates empty versioned indices with aliases before Guppy starts,
without replacing existing indices or inserting synthetic training records.

Tube 2025.08 has no linux/arm64 manifest. ETL therefore uses the multi-architecture
Tube build pinned to sha256:809c8451a2230976965fb3592f9c6ce1f5d70a23955a9da2fdef16b73610303d
(observed under master on 2026-11-12). It does not follow future master updates.
Its application/ETL compatibility still requires a successful live run.
