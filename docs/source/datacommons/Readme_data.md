- What is a data commons?
    * eg: data.midrc.org

- What is a data mesh?
    * Also called a data repository or data ecosystem
    * Contains two or more data commons, data repositories, or knowledge bases
    * Does not hold the data
    * Allows different contributors to provide data to different mesh nodes
    * Example: healdata.org

- What are mesh services?
    * Software services that provide:
        - open APIs for indexing data objects
        - the ability to associate metadata with data
        - control over user access

- What is a data hub?
    * A single point of discovery
    * An interface or API
    * Combines data across data meshes

- What are workspaces?
    * Provide data analysis without requiring data downloads; Jupyter and RStudio are examples
    * Can access more than one data resource
    * Use mesh services for user authentication and authorization

- Gen3 capabilities
    * Data management
        - Ingests data
        - File upload and indexing
    * Data resource access
        - Arborist
    * Data search
        - Guppy
        - GraphQL
        - Explorer UI
        - Discovery UI
    * Data analysis
        - Custom apps
        - Workspaces
        - Task execution service

- Gen3 data management
    * File indexing
    * Structured data indexing
    * Semi-structured data ingestion and aggregation

- Gen3 data access
    * Attribute-based access control through Arborist
    * Manages an whitelist in YAML
    * Structured data access through queries; the Sheepdog service exports structured data tables
    * Structured data queries through Peregrine and Guppy
    * Data model (PostgreSQL/Peregrine) and ETL mapping (Elasticsearch/Peregrine)

- Gen3 data analysis
    * Custom apps
    * Resource browser
        - Tutorials and examples
    * Workspaces
        - Analysis VMs with JupyterLab and RStudio
        - Load notebooks
    * Task execution services
        - Nextflow

GEN 3 Archirecture
--------------------

* Front end 
* back end
* communication interafce between them'

* Front end interact with API
* API interctas with backend
* Microservice architecture
* very floxible - like Lego

*  User jouney: 
    Data doscovery -> 
    Structured data search and submission
    -> Cohort and User data management
    -> data analysis

    - Find the data
    - Filter tha data (subset of data)
    - Attach information about the user
    - Then go to the analysys service

* Discovery page
    - Flexible
    - backend service: meta data service 
    - disovery AI (development ongoing)

* structured data
    - A lot of API and data management automatically generate when defining the data model
    - The data model is in a way a confuguration

* sheepdog
    - handles structured graph submission
    - handle the validation the incoming data gainst theb data model
    - Generates erro r when it doesnt match
    - store the data in PostGres

* Peregrinue
    - Expose the GraphQL intreface over sheepdog database
    - Type in what you receive in the UI and pregerinie queries it accordingly

* Elastic search and Guppy
    - As data grows querying in sheepdog can get intensive
    - You may need t cache a subset of data in a persistence layer
    - Elastic search is used for this 
        * "Extarcts" the data from potsgres 
        * Trasforms it
        * 
    - Guppy sist over the elastic search
    - Exploration page is build on top of guppy 

* UI
    - GEN3 Exploration page
        * daya chohort  building
        * subset of the data
    - Gen3 Query page
        * write graphQl
    - Gen3 data model viwere
        * visualise graph like model
        * explore node and properties
    - Gen3 data submission UI
        * for structures data

* User austhentication and autherization
    - Fence: control Login process and some data acees
        * external identity ius the source of truth. 
        * fence connect to this credentials
     - Arborist- Policy engine
        * defines what can a user access

* analysis
    - Workspace page - jupyter, Rstudio

    
    





    
* Revproxy
    - traffic director
    - no front end component


