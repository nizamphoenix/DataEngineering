import apache_beam as beam
from apache_beam.options.pipeline_options import PipelineOptions

'''
PipelineOptions has configurations for different aspects of your pipeline: runner-type, runner-specific configurations. 
runner: runitme engine that executes pipelines like DataFlow(GCP), samza, flink etc
'''
with beam.Pipeline(options=PipelineOptions()) as p:
  pass
