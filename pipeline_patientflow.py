import argparse
import csv
import logging
import apache_beam as beam
from apache_beam.metrics.metric import Metrics
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

class ParseGameEventFn(beam.DoFn):
  """
  Recommended for  data processing tasks that can be paralleilised
  """
  def __init__(self):
    beam.DoFn.__init__(self)
    self.num_parse_errors = Metrics.counter(self.__class__, 'parse_errors')

  def process(self, elem):
    #overridden method from DoFn, called implicitly when this class is instantiated
    try:
      row = list(csv.reader([elem]))[0]
      yield {       #using yield is efficient,avoids memory explosion
          'id': row[0],
          'name': row[1],
          'age': int(row[2]),
          'admission_timestamp': int(row[3]) / 1000.0,#converting to seconds
      }
    except:
      # Log and count parse errors
      self.num_parse_errors.inc()
      logging.error('Parse error on "%s"', elem)
      
      
      
class HourlyPatientAdmissions(beam.PTransform):
  def __init__(self, start_min, stop_min, window_duration):
    super().__init__()
    beam.PTransform.__init__(self)
    self.start_timestamp = str2timestamp(start_min)
    self.stop_timestamp = str2timestamp(stop_min)
    self.window_duration_in_seconds = window_duration * 60

  def expand(self, pcoll):
    return (
        pcoll
        | 'ParseAdmissionEventFn' >> beam.ParDo(ParseGameEventFn())

        # Filter out data before and after the given times to avoid duplicates.
        | 'FilterStartTime' >>
        beam.Filter(lambda elem: elem['timestamp'] > self.start_timestamp)
        | 'FilterEndTime' >>
        beam.Filter(lambda elem: elem['timestamp'] < self.stop_timestamp)
      
        | 'AddEventTimestamps' >> beam.Map(
            lambda elem: beam.window.TimestampedValue(elem, elem['timestamp']))
        | 'FixedWindowsTeam' >> beam.WindowInto(
            beam.window.FixedWindows(self.window_duration_in_seconds))

      
 

  def run(argv=None, save_main_session=True):
  """Main entry point"""
  parser = argparse.ArgumentParser()

  #maps to files in GCS
  parser.add_argument(
      '--input',
      type=str,
      default='gs://---------------------------------------------',
      help='Path to the data file(s) of patient records.')
  parser.add_argument(
      '--dataset',
      type=str,
      required=True,
      help='BigQuery dataset already exists.')
  parser.add_argument(
      '--table_name',
      default='patients',
      help='BigQuery table already exists.')
  parser.add_argument(
      '--window_duration',
      type=int,
      default=60,
      help='Numeric value of fixed window duration, in minutes')
  parser.add_argument(
      '--start_min',
      type=str,
      default='1970-01-01-00-00',
      help='String representation of the first minute after '
      'which to generate results in the format: '
      'yyyy-MM-dd-HH-mm. Any input data timestamped '
      'prior to that minute won\'t be included in the '
      'sums.')
  parser.add_argument(
      '--stop_min',
      type=str,
      default='2100-01-01-00-00',
      help='String representation of the first minute for '
      'admitting the patient: '
      'yyyy-MM-dd-HH-mm')

  args, pipeline_args = parser.parse_known_args(argv)

  options = PipelineOptions(pipeline_args)

  if options.view_as(GoogleCloudOptions).project is None:
    parser.print_usage()
    print(sys.argv[0] + ': error: argument --project is required')
    sys.exit(1)

  options.view_as(SetupOptions).save_main_session = save_main_session

  with beam.Pipeline(options=options) as p:
    (  
        p
        | 'ReadInputText' >> beam.io.ReadFromText(args.input)
        | 'HourlyAdmissions' >> HourlyTeamScore(
            args.start_min, args.stop_min, args.window_duration)
        | 'AdmissionsDict' >> beam.ParDo(TeamScoresDict())
        | 'WriteTeamScoreSums' >> WriteToBigQuery(
            args.table_name,
            args.dataset,
            {
                'hour_window': 'STRING',
                'total_admissions': 'INTEGER',
                'window_start': 'STRING',
            },
            options.view_as(GoogleCloudOptions).project))




