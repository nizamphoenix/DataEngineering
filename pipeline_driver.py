'''
This is a driver defining pipeline to run on GCP's DataFlow runner.
This driver defines inputs, transforms, and outputs that constitute the pipeline.
'''
import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

'''
PipelineOptions has configurations for different aspects of your pipeline: runner-type, runner-specific configurations. 
runner: runitme engine that executes pipelines like DataFlow(GCP), samza, flink etc
'''
somedata = ['eeeeeeeeeee','brrrr','aerrrrrr','garrrrrr','reaaera','afasfdasf']
with beam.Pipeline(options=PipelineOptions()) as p:
  #1.reading data using beam's api
  lines = p | 'ReadMyFile' >> beam.io.ReadFromText('gs://path_to_file_in_gcs')
  #type(lines)-->PCollection
  #2.reading data from system's memory
  lines = (p | beam.Create(somedata))#Create is a transform
  #A PCollection belongs to the Pipeline object for which it is created.Multiple pipelines cannot share a PCollection object.
