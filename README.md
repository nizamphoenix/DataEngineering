This is a repository for creating pipelines using Apache Beam's Python SDK with GCP DataFlow Runner.  
Apache Beam is a unified framework for creating batch and streaming pipelines.  
Notes:-  
-program to create a pipeline: pipeline driver  
-pipeline driver defines inputs, transforms, and outputs that constitute the pipeline.  
-A pipeline runs on a runner: runitme engine that executes pipelines like DataFlow(GCP), samza, flink etc  
-PipelineOptions: class to configure pipeline for different aspects of your pipeline: runner-type, runner-specific configurations.   
-PTransform: class extended to define transforms, expand method is overridden.  
-DoFn: class extended to define ParDo transforms which are suitable for parallel tasks like extracting,formating data, process method is overridden.  
Reading data into pipeline:-  
1.reading data using beam's api: O/p PCollection = pipeline | beamAPI(i/p PCollection)  
lines = p | 'ReadMyFile' >> beam.io.ReadFromText('gs://path_to_file_in_gcs')  
2.reading data from system's memory: O/p PCollection = pipeline | PCTransform(i/p PCollection)  
lines = (p | beam.Create(somedata))  
