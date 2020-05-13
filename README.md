This is a repository for creating pipelines using Apache Beam's Python SDK with GCP DataFlow Runner.  
Notes:-  

**Apache Beam** is a unified framework for creating batch and streaming pipelines.  
-program to create a pipeline: pipeline driver  
-pipeline driver defines inputs, transforms, and outputs that constitute the pipeline.  
-A pipeline runs on a runner: runitme engine that executes pipelines like DataFlow(GCP), samza, flink etc  
-PipelineOptions: class to configure pipeline for different aspects of your pipeline: runner-type, runner-specific configurations.   
-PTransform: class extended to define transforms, expand method is overridden.  
-DoFn: class extended to define ParDo transforms which are suitable for parallel tasks like extracting,formating data, process method is overridden.  

**Reading data into pipeline:-**  
1. reading data using beam's api: O/p PCollection = pipeline | beamAPI(i/p PCollection)  
   ex:- `lines = p | 'ReadMyFile' >> beam.io.ReadFromText('gs://path_to_file_in_gcs')`    
2. reading data from system's memory: O/p PCollection = pipeline | PCTransform(i/p PCollection)  
   ex:- `lines = (p | beam.Create(somedata))`    

**Writing data to BigQuery with DataFlow**  
Beam SDK includes built-in transforms that can read data from and write data to Google BigQuery tables.
BigQueryIO read and write transforms produce and consume data as a PCollection of dictionaries, 
where each element in the PCollection represents a single row in the table.   
Install relevant sdk with `pip install apache-beam[gcp]`  

1.destination table name.  
2.The destination table’s "create" disposition.  
   -controls whether or not BigQuery write operation should   
       i) create a table if the destination table does not exist(BigQueryDisposition.CREATE_IF_NEEDED);  
       also a schema needs to be provided if not then fails at runtime, or  
      ii) If the destination table does not exist, the write operation fails.(BigQueryDisposition.CREATE_NEVER)  
3.The destination table’s "write" disposition.  
   -The write disposition specifies whether the data you write will  
       i) replace an existing table(BigQueryDisposition.WRITE_TRUNCATE),  
      ii) append rows to an existing table(BigQueryDisposition.WRITE_APPEND), or  
     iii) write only to an empty table(BigQueryDisposition.WRITE_EMPTY).  



