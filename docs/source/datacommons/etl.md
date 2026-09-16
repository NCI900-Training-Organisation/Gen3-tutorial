
Undestanding ETL and ETL mapping
----------------------------

- for displaying data

- roles
    * GEN3 operator
    * Data contributor
    * GEN3 user

- operator in collaboration with the contributor creates the data model
    * make it searchable

- Gen3 workflow
    * Step 1 is createing this data model
    * Step 2 is cleaing all the data
    * Step 3 is the actual submiison of the data

- data is submitted to the Graph database through **sheepdog**
- API request can be made to the postgresSQL throgh peregruine (basically querues the database)
- API request can be made to the Elastic Search throgh Guppy



- imporatnt: submitted data is not used to configure the frontend
- ETL (Extract, trasnform, Load) is waht actually alows it to make it accessible in the front end
- This takes data from the postgres database and load it into the elastic search indeices
- This makes queries fast
- Search on the exploration page directly results from ETL mapping  

- Exploration page -> Guppy query service -> Elastic Search queries -> Elastic search indices
    * Elastic search indices are created from the ETL mapping
    * ETL mapping is directly resultant from the relational database (postgres/sheepdog)
    * Sheepdog database is structures from the data model
    * Why? - as data grows this setup becaomes more performant


- Tube
    * Microsercice that travels across graphs to find and grab adata in PotsgresSQL
    * transforms it into  ElasticSearch indexed documents
    * indices alloes micrtoservices Guppy to qhuckly query the data
    * controls what data is gathered (using etlMapping.yaml)
        - Tells which tables and fields to ETL

- Tube working
    * data model / data dictinary
    * ETL mapping
    *  Apache spark  cluster
        - SQOOP interacrts with postgres (sheepdog) to extarct data
        - SQOOP temporarily dumb it  Hadoop
        - Apache spark then rfeads data from Hadoop and traforms it according to ETL config. This creates inices in the elastic search

ETL mapping Syntax
---------------------


The generic syntax reference is available in
[`etlMapping.example.yaml`](manifest/etlMapping.example.yaml). It shows the fields that an ETL mapping can hold.

- name: Name the index will have in elastic search
- doc_type: Name guppy will use for queryinh the index
- Type:
    * agrrgator: inidcate **root** node in the DB
        - node can be thought as a table in posgress that contains all data
    * collector: inidcate **category** node to collect propoertes from 
        - In this case instead of single nodes, it can be thoght of as a collection of similar type of nodes (eg: alll data file nodes)
- props: fields that are expected to be in the final elastic serach index
    * Everyy peoperty should have a name
    * if prop name is different in the graph, specify the name of the property in the source DB (src)
    * value_mapping is used to map new valu name to the existing values in the DB. eg: F to Female

- ETL mappiung support 6 functuon, It can be used by aggregators and collection
    * fn: count - counting how manynodes have values for that prop per case/root
    * fn: max - reporting the max value among records for that property for a case/root
    * fn: min - reporting the min value among records for that property for a case/root
    * fn: sum - reporting the sum of values for records for that property
    * fn: list - the full set of values (including any duplicates) for records for that property
    * fn: set - reporting all the unique values for records for that property

- Types of mapping
    * aggregation
        - creates aggregators
        - Traveling from a single root node, aggregators gather data from properties on connected nodes into a single index in ES
        - Eg: a case aggregator that collects selected clinical data properties from the case node through the clinical nodes on a data model
    * Injection
        - creates collectors
        - Collectors travel across multiple nodes of the same node category to gather data from shared properties on the nodes, and “inject” a parent node's ID into downstream nodes for faster joining
        - Eg: a data file collector that collects data from properties on many different file nodes

- mapping sub types
    * flatten_props: Get props from lower nodes
    * parent_props: Get props from upper nodes
    * nested_props: Get props from multiple lower nodes
    * aggregated_props: Add statistics into indices
    * joining_props: Join properties between indices

Example data model
---------------------

![Example GEN3 data model](images/16-example-data-model.png)

Creating a mapping
---------------------

![ETL mapping](images/17-flatten-props-one-to-one.png)

The mapping shown in the image is also available as
[`flatten-props-one-to-one.example.yaml`](manifest/flatten-props-one-to-one.example.yaml):

```yaml
mappings:
    - name: simple_flatten # Elasticsearch index name
        doc_type: subject    # document type - used to query the index
        type: aggregator
        root: subject
        props:
            - name: submitter_id
        flatten_props:
            - name: subject_demographics
                path: demographics
                props:
                    - name: age
                    - name: race
```

- flatten propos
- we are going to flatten demographics into subjects
- name (for elastic search) is **simple_flatten**
- name for guppy is **subject**
- root node is **subject** (as in the data model)
- we are going to pull the **submitter_id** (our props) out of the subject into the index
- our sub mapping type is **falletn_props**
    * the index **subject_demographics**  will be  created
    * we specif the the path (in the model it is Subject -> Demographics)
    * Fom demographics **age** and **race** will be pulled in and flattened

- Now we will get this sample index

Example Index:

| Subject.submitter_id | demographics.age | demographics.race |
|---|---:|---|
| sub_123 | 18 | Black or African American |
| sub_456 | 89 | Asian |


![ETL mapping](images/18-flatten-props-many-to-star.png)

[`flatten-props-many-to-star.example.yaml`](manifest/flatten-props-many-to-star.example.yaml):

```yaml
mappings:
    - name: flatten_props_multi # Elasticsearch index name
        doc_type: subject
        type: aggregator
        root: subject
        props:
            - name: submitter_id
        flatten_props:
            - name: subject_events
                path: events
                props:
                    - name: date
                    - name: type
                sorted_by: date, desc
```

Example Index:

| Subject.submitter_id | date | type |
|---|---|---|
| ~~sub_123~~ | ~~03/20/1986~~ | ~~birth~~ |
| sub_123 | 03/20/2009 | hospitalization |
| ~~sub_456~~ | ~~07/26/2025~~ | ~~hospitalization~~ |
| sub_456 | 08/26/2025 | death |

Parent props:

![ETL mapping](images/19-parent-props.png)

The parent-props mapping is also available as
[`parent-props.example.yaml`](manifest/parent-props.example.yaml):

```yaml
mappings:
    - name: my-data-commons_subject # Elasticsearch index name
        doc_type: subject
        type: aggregator
        root: subject
        props:
            - name: submitter_id
        parent_props:
            - name: subject_study
                path: study
                props:
                    - name: data_batch
```

Example Index:


| Subject.submitter_id | data_batch |
|---|---|
| sub_123 | NIH_08262025 |
| sub_456 | NSRR_08272025 |


![ETL mapping](images/20-nested-props.png)

The nested-props mapping is also available as
[`nested-props.example.yaml`](manifest/nested-props.example.yaml):

```yaml
mappings:
    - name: my-data-commons_subject
        doc_type: subject
        type: aggregator
        root: subject
        props:
            - name: submitter_id
        nested_props:
            - name: subject_samples
                path: sample
                props:
                    - name: submitter_id
                    - name: collection_date
                    - name: sample_type
                nested_props:
                    - name: sample_data-file
                        path: data_file_image
                        props:
                            - name: file_size
                            - name: md5sum
```

Example nested index shape:

```json
{
    "subject": [
        {
            "submitter_id": "sub_123",
            "samples": [
                {
                    "submitter_id": "sample_id_123",
                    "collection_date": "08/26/2024",
                    "sample_type": "assay",
                    "data_files": [
                        {
                            "file_size": "100 MB",
                            "md5sum": "e33n..."
                        }
                    ]
                }
            ]
        }
    ]
}
```

- We are travelling from **Subject** to **Data File**
- So we need to nest **Sample** -> **Data File- Image**
- We can skip nodes when travelling down the graph

![Nested props skipping nodes](images/21-nested-props-skipping-nodes.png)

The skipping-nodes mapping is also available as
[`nested-props-skipping-nodes.example.yaml`](manifest/nested-props-skipping-nodes.example.yaml):

```yaml
mappings:
    - name: my-data-commons_subject
        doc_type: subject
        type: aggregator
        root: subject
        props:
            - name: submitter_id
        nested_props:
            - name: subject_samples
                path: sample.data_file_image
                props:
                    - name: file_size
                    - name: md5sum
```

The dotted path skips the `sample` node and collects properties directly from
its `data_file_image` child nodes.


![Nested props skipping nodes](images/21-nested-props-skipping-nodes.png)

![Aggregated props](images/22-aggregated-props.png)

- we are counting the number of samples per **subject**
- root is **subject**
- We are pulling some data from sample and the sample counts


The aggregated-props mapping is also available as
[`aggregated-props.example.yaml`](manifest/aggregated-props.example.yaml):

```yaml
mappings:
    - name: my-data-commons_subject
        doc_type: subject
        type: aggregator
        root: subject
        props:
            - name: submitter_id
        nested_props:
            - name: subject_samples
                path: sample
                props:
                    - name: collection_date
                    - name: sample_type
        aggregated_props: # used to get aggregate statistics of
            - name: sample_count
                path: samples # path to node from root
                fn: count
```

Example Index:

| Subject.submitter_id | collection_date | sample_type | sample_count |
|---|---|---|---:|
| sub_123 | 08/26/2025 | assay | 3 |
|  | 08/26/2025 | imaging | 3 |
|  | 09/01/2025 | assay | 3 |
| sub_456 | 07/26/2024 | imaging | 3 |
|  | 08/23/2025 | imaging | 3 |
|  | 08/23/2025 | assay | 3 |


- All the above has been aggrgator types
- Next we will look into injection

![Injecting props](images/23-injecting-props.png)

- inject **subject_id** into the catogory **data_file**
- fn:set

The injecting-props mapping is also available as
[`injecting-props.example.yaml`](manifest/injecting-props.example.yaml):

```yaml
mappings:
    - name: data-file_subject
        doc_type: data_file
        type: collector
        category: data_file
        props:
            - name: submitter_id
        injecting_props:
            subject:
                - fn: set
                    name: _subject_id # note the preceding "_"
                    src: subject_id
```

Example Index: data files with injected subject IDs

| Data_files_image.submitter_id | _subject_id |
|---|---|
| image_123 | subject_123 |
| image_234 | subject_123 |
| image_345 | subject_123 |
| image_456 | subject_345 |
| image_567 | subject_345 |
| image_678 | subject_345 |

| Data_files_assay.submitter_id | _subject_id |
|---|---|
| assay_123 | subject_567 |
| assay_234 | subject_567 |
| assay_345 | subject_567 |
| assay_456 | subject_789 |
| assay_567 | subject_789 |
| assay_678 | subject_789 |

![Joining props](images/25-joining-props.png)

The joining-props mappings are also available as
[`joining-props.example.yaml`](manifest/joining-props.example.yaml):

```yaml
mappings:
    - name: data-file_study
        doc_type: data_file
        type: collector
        category: data_file
        props:
            - name: submitter_id
        injecting_props:
            study:
                - props:
                        - fn: set
                            name: study_id
                            src: study_id

    - name: sample_for_join
        doc_type: subject
        type: aggregator
        root: events
        props:
            - name: event_id
        joining_props:
            - index: data-file_study
                join_on: study_id
                props:
                    - fn: set
                        name: study_id
                        src: study_id
```

Example Index:

| events.submitter_id | study_id | data_file.submitter_id |
|---|---|---|
| event_1 | study_1 | wb54yt4byw5b3 |
| event_2 | study_1 | sasdffv sdfgsrg |
| event_3 | study_1 | gd4qbg5gw545s |
| event_1 | study_2 | ds43w5bg b45try |
| event_2 | study_2 | aq4bqbtqnbq4wt4 |
| event_3 | study_2 | 45q4g5w5rgw545 |


Putting this together
---------------------

![Manifest](images/26-building-a-file-manifest.png)


- Create file manifest
- In this example we want a search to be able to capture what data files are present for
    * studies,
    * subjects and
    * demographics

- The steps involved in this will be
    * Create an Aggregator index connecting Subject with Demographics and Sample (nested)
    * Create an collector (injected) index with the Data File nodes
    * Join the file index to the aggregator to build a file manifest

![Subject file manifest mapping](images/27-subject-file-manifest-mapping.png)

The complete subject-file manifest mapping is also available as
[`subject-file-manifest.example.yaml`](manifest/subject-file-manifest.example.yaml):

```yaml
mappings:
    - name: file_manifest
        doc_type: subject
        type: aggregator
        root: subject
        props:
            - name: submitter_id
        nested_props:
            - name: demographic
                path: demographic
                props:
                    - name: race
                    - name: age
            - name: sample
                path: sample
                props:
                    - name: collection_id
                    - name: sample_type
        joining_props:
            - index: file
                join_on: _subject_id
                props:
                    - name: object_id
                        src: object_id
                        fn: set

    - name: file_collector
        doc_type: file
        type: collector
        root: None
        category: data_file
        props:
            - name: submitter_id
            - name: object_id
            - name: md5sum
            - name: file_size
        injecting_props:
            subject:
                props:
                    - name: _subject_id
                        src: id
```

- IMPORTANT: guppy and the explorer config should match with the ETL mapping
   
Troubleshooting ETL
-----------------------

- Sanity checks

    * Did you deploy the new ETL mapping?
    * Did you make sure to run the ETL after deploying the new ETL mapping?
    * Did you re-roll Guppy after your ETL run?
    * If so – were there any Guppy errors at startup? Check both your Guppy and
    Portal/FEF logs to see if there are any errors (eg, new portal pod may not be
    deployed because of a simple JSON parsing error).
    * Did you update the Portal/FEF explorer config to make sure it is aligned with any new data in ES and accessed by Guppy?

- check ETL logs
    * kubectl logs <etl pod name> -c tube -f

- Log to ES pod
    * kubectl exec -it <es proxy pod> -- sh

- To check what indices are present in your ES - In two terminals, do the following:
    * port forward ES service: kubectl port-forward svc/elasticsearch 9200:9200
    * See data in all indices in ES: curl -X GET http://localhost:9200/_cat/indices
    * See data in a specific index: curl -X GET http://localhost:9200/<index name>






- If your data is in ES - you know ETL is working and data is being created in ES

- If your data is NOT in ES:
    * Your ETL has a problem. The ETL log should provide a clue about whatʼs wrong - you can tell from the logging before it failed where in the ETL mapping it had the failure.
    * Examine your ETL mapping; check if there's anything that could be a typo or an incorrect prop name or path.
    * Look at your data in Sheepdog. Particularly look for “special characters” (backslash and non-ASCII characters), especially if itʼs a particular data column missing.
    * Confirm with Peregrine queries that the path to the prop you included in the mapping is a valid path.

- Check guppy
    * Check the data can be queried by Guppy - Frontend
    * Once you know the data is in ES - restart Guppy, and check that Guppy can pull data from
    ES. This will help you determine whether the data in ES is queryable by Guppy from the /graphql API.


![Troubleshooting Guppy frontend queries](images/37-troubleshooting-guppy-frontend-queries.png)


![Viewing Guppy schema with mapping query](images/39-viewing-guppy-schema-with-mapping-query.png)
- Check the data can be queried by Guppy (Backend)
    * To log onto your Guppy pod: kubectl exec -it <guppy pod> -- sh
    * Use curl to create a graphql query. For example, here is a sample Guppy query (h/t Joshua Harris)


![Viewing Guppy schema with mapping query](images/39-viewing-guppy-schema-with-mapping-query.png)


- If the data cannot be queried by Guppy:
    * Guppy logs should be helpful here.
    * Check your Guppy config. Make sure the index names (type) in the Guppy config match up, with no typos, to the doc_type fields in the ETL mapping config.
    * Check the JSON structure for problems. (Remember to re-roll Guppy after any config changes before testing if it fixed the problem).
    * Check your Guppy config for appropriate tier_access_level





![Troubleshooting Guppy frontend queries](images/37-troubleshooting-guppy-frontend-queries.png)

![Viewing Guppy schema with mapping query](images/39-viewing-guppy-schema-with-mapping-query.png)

- check the frint end
    * use developer tool in chrome
        - network tab: check the hraphql queries - 200 means the fetch was success . Other wise there i some error
        - Patyoad tab - check the query, jason

![Troubleshooting frontend network requests](images/42-troubleshooting-frontend-network-requests.png)

![Troubleshooting GraphQL query payloads](images/43-troubleshooting-graphql-query-payloads.png)















