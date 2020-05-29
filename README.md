This is a repository for creating pipelines using Apache Beam's Python SDK with GCP DataFlow Runner.  
Notes:-  

*Apache Beam* is a unified framework for creating batch and streaming pipelines.  
- program to create a pipeline: pipeline driver  
- pipeline driver defines inputs, transforms, and outputs that constitute the pipeline.  
- A pipeline runs on a runner: runitme engine that executes pipelines like DataFlow(GCP), samza, flink etc  
- PipelineOptions: class to configure pipeline for different aspects of your pipeline: runner-type, runner-specific configurations.   
- PTransform: class extended to define transforms, expand method is overridden.  
- DoFn: class extended to define ParDo transforms which are suitable for parallel tasks like extracting,formating data, process method is overridden.  

**Reading data into DataFlow pipeline:-**  
- reading data using beam's api: O/p PCollection = pipeline | beamAPI(i/p PCollection)  
   ex:- `lines = p | 'ReadMyFile' >> beam.io.ReadFromText('gs://path_to_file_in_gcs')`    
- creating & reading data from system's memory: O/p PCollection = pipeline | PCTransform(i/p PCollection)  
   ex:- `lines = (p | beam.Create(somedata))`    
- reading data, specifically, from Pub/Sub: O/p PCollection = pipeline | beamAPI(i/p PCollection)  
   ex:- `lines = (p | beam.io.ReadStringsFromPubSub(topic= projectid.topicname ))`  

**Writing data to BigQuery with DataFlow:-**  
Beam SDK includes built-in transforms that can read data from and write data to Google BigQuery tables.
BigQueryIO read and write transforms produce and consume data as a PCollection of dictionaries, 
where each element in the PCollection represents a single row in the table.   
Install relevant sdk with `pip install apache-beam[gcp]`  

The following are required to facilitate the transfer:-  
- destination table name.  
- The destination table’s "create" disposition: controls whether or not BigQuery write operation should,     
  -  create a table if the destination table does not exist(BigQueryDisposition.CREATE_IF_NEEDED);  
       also a schema needs to be provided if not then fails at runtime, or  
  -  If the destination table does not exist, the write operation fails.(BigQueryDisposition.CREATE_NEVER)  
- The destination table’s "write" disposition: controls whether the data you write will.    
  -  replace an existing table(BigQueryDisposition.WRITE_TRUNCATE),  
  -  append rows to an existing table(BigQueryDisposition.WRITE_APPEND), or  
  -  write only to an empty table(BigQueryDisposition.WRITE_EMPTY).  

**Data transfer to & fro Cloud storage**
- Cloud connector facilitates high speed transfers, hence used by Dataproc to execute spark & hadoop jobs  
- Transfer appliance  
- Storage transfer service  
- gsutil 
- distcp, running on cloud connector
