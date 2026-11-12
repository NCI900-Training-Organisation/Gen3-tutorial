-- Read the service password from the PostgreSQL pod's Secret-backed environment.
\set ON_ERROR_STOP on
\getenv service_password GEN3_SERVICE_PASSWORD
SELECT format('CREATE ROLE %I LOGIN PASSWORD %L', name, :'service_password')
FROM (VALUES ('fence_gen3'), ('arborist_gen3'), ('indexd_gen3'), ('sheepdog_gen3'), ('peregrine_gen3')) roles(name)
WHERE NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = name)
\gexec
SELECT format('CREATE DATABASE %I OWNER %I', db, owner)
FROM (VALUES ('fence','fence_gen3'), ('arborist','arborist_gen3'), ('indexd','indexd_gen3'), ('sheepdog','sheepdog_gen3')) dbs(db,owner)
WHERE NOT EXISTS (SELECT 1 FROM pg_database WHERE datname = db)
\gexec
GRANT sheepdog_gen3 TO peregrine_gen3;
