'''
Using Dataflow to read from and write to BigQuery.
Beam SDK includes built-in transforms that can read data from and write data to Google BigQuery tables.
BigQueryIO read and write transforms produce and consume data as a PCollection of dictionaries, 
where each element in the PCollection represents a single row in the table.


use pip install apache-beam[gcp] to use BigQuery I/O
'''


from apache_beam.io.gcp.internal.clients import bigquery

table_spec = bigquery.TableReference(
    projectId='project_name',
    datasetId='bigquery_dataset_name',
    tableId='bigquery_table_name')


# 1. reads an entire table that contains patient data and then extracts the patient_count column
patient_count = (
    p
    | 'ReadTable' >> beam.io.Read(beam.io.BigQuerySource(table_spec))
    | beam.Map(lambda elem: elem['patient_count'])
)

# 2. reads only the query string and then extracts the patient_count column
patient_count = (
    p
    | 'QueryTable' >> beam.io.Read(beam.io.BigQuerySource(
        query='SELECT patient_count FROM '\
              '`project_name:bigquery_dataset_name.bigquery_table_name`',
        use_standard_sql=True#set to False if legacy SQL [] is used
    ))
    | beam.Map(lambda elem: elem['patient_count'])
)

#3. When writing to BigQuery, the following information must be provided:
a = {
    'fields': [{
        'name': 'patient_name', 'type': 'STRING', 'mode': 'REQUIRED'
    }, {
        'name': 'age', 'type': 'INTEGER', 'mode': 'REQUIRED'
    }]
}
records = p | beam.Create([ #PCollection of dictionaries, each is a row
    {
        'patient_name': 'Spoc', 'age': 67
    },
    {
        'patient_name': 'Yoda', 'age': 30
    },
])


records | beam.io.WriteToBigQuery(
    table_spec,
    schema=table_schema,
    write_disposition=beam.io.BigQueryDisposition.WRITE_TRUNCATE,
    create_disposition=beam.io.BigQueryDisposition.CREATE_IF_NEEDED
)
