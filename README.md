This is a repository for creating pipelines using Apache Beam's Python SDK with GCP DataFlow Runner and contains short notes of GCP data products.   

Notes:-  

**Apache Beam** is a unified framework for creating batch and streaming pipelines.  
- program to create a pipeline: pipeline driver  
- pipeline driver defines inputs, transforms, and outputs that constitute the pipeline.  
- A pipeline runs on a runner: runitme engine that executes pipelines like DataFlow(GCP), samza, flink etc  
- PipelineOptions: class to configure pipeline for different aspects of your pipeline: runner-type, runner-specific configurations.   
- PTransform: class extended to define transforms, expand method is overridden.  
- DoFn: class extended to define ParDo transforms which are suitable for parallel tasks like extracting,formating data, process method is overridden.  

### Reading data into DataFlow pipeline:-
- reading data using beam's api: O/p PCollection = pipeline | beamAPI(i/p PCollection)  
   ex:- `lines = p | 'ReadMyFile' >> beam.io.ReadFromText('gs://path_to_file_in_gcs')`    
- creating & reading data from system's memory: O/p PCollection = pipeline | PCTransform(i/p PCollection)  
   ex:- `lines = (p | beam.Create(somedata))`    
- reading data, specifically, from Pub/Sub: O/p PCollection = pipeline | beamAPI(i/p PCollection)  
   ex:- `lines = (p | beam.io.ReadStringsFromPubSub(topic= projectid.topicname ))`  

### Writing data to BigQuery with DataFlow:-  
Beam SDK includes built-in transforms **BigQuery I/O connector** that can read data from and write data to Google BigQuery tables.
BigQueryIO read and write transforms produce and consume data as a PCollection of dictionaries, 
where each element in the PCollection represents a single row in the table.   
Install relevant sdk with `pip install apache-beam[gcp]`  

The following are required to facilitate the transfer:-  
- destination table name.  
- The destination table’s "create" disposition: controls whether or not BigQuery write operation should,     
  -  create a table if the destination table does not exist(BigQueryDisposition.CREATE_IF_NEEDED);  
       also a schema needs to be provided if not then fails at runtime, or  
  -  exit with a fail status if the destination table does not exist.(BigQueryDisposition.CREATE_NEVER)  
- The destination table’s "write" disposition: controls whether the data you write will.    
  -  replace an existing table(BigQueryDisposition.WRITE_TRUNCATE),  
  -  append rows to an existing table(BigQueryDisposition.WRITE_APPEND), or  
  -  write only to an empty table(BigQueryDisposition.WRITE_EMPTY).  

### Data transfer to & from Cloud storage  
- Transfer appliance, for one time transfers  
- Storage transfer service, for regular, or transfers from other cloud vendors  
- gsutil 
- distcp, running on cloud storage connector  
*note:-* Cloud storage connector facilitates petabyte/sec transfers, and is used by many GCP services to execute commands to execute tasks; for instance it is used by Cloud Dataproc to execute spark & hadoop jobs on data stored in cloud storage & hence upholding the principle of separating storage from compute.  


### Preemptible worker nodes in Dataproc:-  
- Only use preemptible nodes for jobs that are fault-tolerant or low priority ones such that occasional job failure won't disrupt the business.  
- In general, the more preemptible nodes used relative to standard nodes, the higher the chances are that the job won't have enough nodes to complete the task. The best ratio of preemptible to regular nodes for a job can be found by experimenting with different ratios and analyzing the results.  
- SSDs are not available on preemptible worker nodes. If SSDs are used on dedicated nodes, then any preemptible worker nodes used will have no SSDs available.  


### BigQuery - federated queries:-  
Instead of loading the data, we can create a table that **references** the external(federated) data source & query *directly* even though the data is not stored in BigQuery.  

BigQuery supports the following federated data sources,  
   - Bigtable  
   - Cloud storage  
   - Google drive  
   - Cloud SQL(beta)  
The supported file formats are Avro,CSV,JSON(newline delimited only),ORC,Parquet.  

Few limitations are,  
   - we cannot reference an external data source in a wildcard table query  
   - query results are not cached  
   - Bigtable option is available in certain regions only.  
   
Also, if the BigQuery dataset that is created as a **reference** is in a regional location, the Cloud Storage bucket/BigTable containing the data to be queried **must** be in a regional bucket in the same location, likewise for multi regional buckets; however, this doesn't apply to Google drive. It is sensible to relocate BigQuery dataset rather than the federated source.  

To create and maintain a connection resource, the user must have **bigquery.admin** role.  
When BigQuery connection API is enabled, a service account is automatically created and is used to establish the connection with the federated source.  

BigQuery supports querying **externally partitioned** data in Avro, Parquet, ORC, JSON and CSV formats that is stored in **Cloud Storage** using a default *hive(warehouse)* partitioning layout.  

BigQuery supports queries against both personal & shared Google Drive files with CSV,JSON(newline delimitted),Avro,Google sheets formats.   

BigQuery supports creation of permanent & temporary tables for Bigtable, cloud storage & drive, followed by querying by combining a table definition file, inline schema definition, json schema definition; while BigQuery support only temporary table creation with Cloud SQL using *EXTERNAL_QUERY()* function `SELECT * FROM EXTERNAL_QUERY(connection_id, external_database_query);` 


### Loading data into BigQuery:-  
It is necessaray to load data into BigQuery as datasets before querying it if the data is not accessable to BigQuery, the data is loaded into a *new table or partition*; however, one may need **not load** data into BigQuery in scenarios like public datasets, shared datasets, federated data sources(if speed is not priority), logging files.  

An aside:- log files can be exported to Cloud Storage, BigQuery, or Pub/Sub.  

BigQuery allows to load data from:-  
  - Cloud Storage  
  - Google services(SaaS) like Ad Manager, Ads, YouTube channel reports using   
  - local machine  
  - streaming inserts i.e. inserting one data instance at a time  
  - DML inserts performing bulk inserts  
  - Dataflow writes using BigQuery I/O transforms  
The supported file formats are CSV, Avro, Parquet, ORC, JSON, Firestore exports, Datastore exports.  

- When data is loaded into BigQuery, it is converted into columnar format, BigQuery's storage format.  
- BigQuery encodes data in UTF-8, if it can't then it represents the character by a �  
- Avro binary format is the *preferred* format for loading both compressed and uncompressed data; parquet, ORC are also good but not preferred; CSV,JSON are used if data is uncompressed and if bandwidth is less then compress with **gzip** only.  
- Schema auto-detection is available forJSON or CSV files but unavaibale for Avro files, ORC files, Parquet files, Datastore exports,Firestore exports.  
- **BigQuery Data transfer service** automatically schedules and manages recurring data loads into BigQuery from Cloud Storage, Google Saas, other vendors(Amazon S3), othe data warehouses.  
- Wildcard can be used to load multiple files from Cloud Storage, but this option is not available while loading files from local machine.  

### Exporting data from BigQuery:-  
 data can be exported from BigQuery in multiple formats to Cloud storage only, in chunks of 1GB files, if size is more than 1GB then wildcard characters are used to name files; also DataFlow can be utilised to write a job instead of manually transfering files.  

### Partitioned tables in BigQuery:-  
It improves query performance, and controls costs by reducing the number of bytes read by a query.  

BigQuery tables can be partitioned(reorganised by creating *logical* segments) based on  
- ingestion time: data's ingestion (load) date or arrival date  
  - such tables include a pseudo column named *_PARTITIONTIME* that contains a date-based timestamp  
  - queries against such tables can restrict the data read by supplying *_PARTITIONTIME* filter in query  
  - partitions have the same schema definition as the table  
- timestamp/Date: based on TIMESTAMP or DATE type(s) column  
  - Each partition created in such table can be considered as a single day of calendar year  
  - Also 2 special partitions are created:  
    - __NULL__ partition: represents rows with NULL values in the partitioning column  
    - __UNPARTITIONED__ partition: represents rows whose DATE column values exists outside the allowed range of dates  
  - queries against such tables can restrict the data read by supplying *appropriate dates* filter in query  
- Integer range: based on Integer type(s) column  
  - create partitions based on a specific INTEGER column, with our choice of start, end, and interval values  
  - Again like timestamp partition, 2 special partitions are created:  
    - __NULL__ partition: represents rows with NULL values in the partitioning column  
    - __UNPARTITIONED__ partition: represents rows whose DATE column values exists outside the allowed range of dates  
    
    
### Clustered tables in BigQuery:-  
- Table data is automatically re-organized into clusters(partitions) based on the contents of one or more columns.  
- Currently, BigQuery allows clustering over a **partitioned table** and is not possible for unpartitioned tables.
- When clustering a table using multiple columns, the order of columns is important since it determines the sort order of the data.  
- The values of clustering columns are used to organize the data into multiple blocks(like index) in BigQuery storage.  
- Clustering can improve the performance of queries that use *filter clauses* or *aggregate clauses* . 
- When a query is submitted that contains a filter clause based on the clustering columns, BigQuery uses the sorted blocks(like index) to eliminate scans of unnecessary data.




### Integer range partitioning v/s clustering:-  
Both improve query performance and reduce query cost by reducing number of bytes read.  

- Use integer range partitioning if,  
  - how the data will be partitioned & ranges used to partition the table are known beforehand.  
  - query cost is **known** before query runs. *dry run* available.  
  - we like to refer a partition during querying, such as to load data to a specific partition, or delete data from a   specific partition.  
  
- Use clustering if,
  - Do not care how the table will be clustered and hence datais clustered. BigQuery automatically figure out how the data should be clustered for optimal performance and cost.  
  - query cost is **unknown** before query runs.  *dry run* unavailable.  
  - Require more than 4,000 partitions since BigQuery has a limit of 4,000 partitions for a partitioned table. No limit for the number of clusters in a table.  


### BigTable imports & exports:-  
- Dataflow templates are used to export data from Cloud Bigtable as Avro/Parquet/Sequence files and then import the data back into Cloud Bigtable. Also, CSV imports are available but exports aren't.  
- The Cloud Dataflow connector(part of beam sdk) for Cloud Bigtable is used.  
- much similar to hbase.  

