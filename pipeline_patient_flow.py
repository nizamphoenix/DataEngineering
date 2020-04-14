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

        # Extract and sum teamname/score pairs from the event data.
        | 'ExtractAndSumScore' >> ExtractAndSumScore('team'))


