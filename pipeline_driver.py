'''
Batch processing pipeline:-
1.reading input from local machine.
2.Extracting data with ParDo transfrom.
3.Applying composite transforms to compute useful information--scores.
4.writing output to a text file.

python scores.py \
    --output gs://$BUCKET/scores/output \
    --runner DataflowRunner \
    --project $PROJECT_ID \
    --region $REGION_ID \
    --temp_location gs://$BUCKET/scores/temp
'''

# source: googlecloudtraining

from __future__ import absolute_import
from __future__ import division

import argparse
import csv
import logging

import apache_beam as beam
from apache_beam.metrics.metric import Metrics
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions


class ParseGameEventFn(beam.DoFn):
  """
  Recommended when data processing, such as first stage, can be done in parallel
  """
  def __init__(self):
    beam.DoFn.__init__(self)
    self.num_parse_errors = Metrics.counter(self.__class__, 'num_parse_errors')

  def process(self, elem):
    #overridden method from DoFn, called implicitly when this class is instantiated
    try:
      row = list(csv.reader([elem]))[0]
      yield {       #using yield is efficient,avoids memory explosion
          'user': row[0],
          'team': row[1],
          'score': int(row[2]),
          'timestamp': int(row[3]) / 1000.0,#converting to seconds
      }
    except:
      # Log and count parse errors
      self.num_parse_errors.inc()
      logging.error('Parse error on "%s"', elem)



class ExtractAndSumScore(beam.PTransform):
  """
  A transform to extract key/score information and sum the scores.
  """
  def __init__(self, field):
    beam.PTransform.__init__(self)
    self.field = field #determines whether 'team' or 'user' info is extracted.

  def expand(self, pcoll):
    #expand() function is overrided from PTransform, and is called implicitly when constructor of this class is invoked
    return (
        pcoll
        | beam.Map(lambda elem: (elem[self.field], elem['score']))
        | beam.CombinePerKey(sum)
    )



class UserScore(beam.PTransform):
  def expand(self, pcoll):
    #expand() function is overrided from PTransform
    return (
        pcoll
        | 'ParseGameEventFn' >> beam.ParDo(ParseGameEventFn())
        # Extract and sum username/score pairs from the event data.
        | 'ExtractAndSumScore' >> ExtractAndSumScore('user')
    )


def format_user_score_sums(user_score):
    '''
    utility function
    '''
    (user, score) = user_score
    return 'user: %s, total_score: %s' % (user, score)

def run(argv=None, save_main_session=True):
  """Main entry point; defines and runs the user_score pipeline."""
  parser = argparse.ArgumentParser()

  # The default maps to two large Google Cloud Storage files (each ~12GB)
  # holding two subsequent day's worth (roughly) of data.
  parser.add_argument(
      '--input',
      type=str,
      default='gs://apache-beam-samples/game/gaming_data*.csv',
      help='Path to the data file(s) containing game data.')
  parser.add_argument('--output', type=str, required=True, help='Path to the output file(s).')

  args, pipeline_args = parser.parse_known_args(argv)

  options = PipelineOptions(pipeline_args)

  # We use the save_main_session option because one or more DoFn's in this
  # workflow rely on global context (e.g., a module imported at module level).
  options.view_as(SetupOptions).save_main_session = save_main_session

  with beam.Pipeline(options=options) as p:
    (  
        p
        | 'ReadInputText' >> beam.io.ReadFromText(args.input)       #reading input from local machine.
        | 'UserScore' >> UserScore()                                #Extracting data with ParDo transfrom.
        | 'FormatUserScoreSums' >> beam.Map(format_user_score_sums) #Applying composite transforms to compute useful information.
        | 'WriteUserScoreSums' >> beam.io.WriteToText(args.output)  #writing output to a text file.
    )

if __name__ == '__main__':
  logging.getLogger().setLevel(logging.INFO)
  run()
