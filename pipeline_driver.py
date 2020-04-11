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
options = PipelineOptions()
google_cloud_options = options.view_as(GoogleCloudOptions)
google_cloud_options.project = 'simple-data-pipelines'
google_cloud_options.job_name = 'countjob'
google_cloud_options.staging_location = 'gs://--------/staging'
google_cloud_options.temp_location = 'gs://----------------/temp'
options.view_as(StandardOptions).runner = 'DataflowRunner'


with beam.Pipeline(options=PipelineOptions()) as p:
  #1.reading data using beam's api
  #lines = p | 'ReadMyFile' >> beam.io.ReadFromText('gs://path_to_file_in_gcs')
  #type(lines)-->PCollection
  #2.reading data from system's memory
  #lines = (p | beam.Create(somedata))#Create is a transform 
  # O/p PCollection = i/p PCollection | PCTransform
  #A PCollection belongs to the Pipeline object for which it is created.Multiple pipelines cannot share a PCollection object.
  p 
  | beam.io.ReadFromText('gs://dataflow-samples/shakespeare/kinglear.txt')
  | 'ExtractWords' >> beam.FlatMap(lambda x: re.findall(r'[A-Za-z\']+', x))
  | beam.combiners.Count.PerElement()
  | beam.MapTuple(lambda word, count: '%s: %s' % (word, count))
  | beam.io.WriteToText('gs://my-bucket/counts.txt')

  result = p.run()
