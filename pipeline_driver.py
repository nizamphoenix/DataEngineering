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
  
  
class ExtractAndFormat(beam.PTransform):
  """
  A transform to extract key/score information and sum the scores.
  The constructor argument `field` determines whether 'team' or 'user' info is extracted.
  """
  def __init__(self, field):
    super().__init__()
    beam.PTransform.__init__(self)
    self.field = field

  def expand(self, pcoll):
    return (
        pcoll
        | beam.Map(lambda x: (x[self.field], x['score']))
        | beam.CombinePerKey(sum))
  
  
def run(argv=None, save_main_session=True):

  parser = argparse.ArgumentParser()
  parser.add_argument(
      '--input',
      type=str,
      default='**************',
      help='absolute path to data files.')
  parser.add_argument(
      '--output', type=str, required=True, help='Path to the output file(s).')

  args, pipeline_args = parser.parse_known_args(argv)

  options = PipelineOptions(pipeline_args)
  options.view_as(SetupOptions).save_main_session = save_main_session

  with beam.Pipeline(options=options) as p:

    def format_user_score_sums(user_score):
      (user, score) = user_score
      return 'user: %s, total_score: %s' % (user, score)

    ( 
        p
        | 'ReadInputText' >> beam.io.ReadFromText(args.input)
        | 'UserReport' >> UserReport()
        | 'FormatPattientReports' >> beam.Map(format_patient_reports)
        | 'WriteUserReports' >> beam.io.WriteToText(args.output))
