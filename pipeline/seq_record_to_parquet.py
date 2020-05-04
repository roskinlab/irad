#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import itertools
import io

import fastavro
import pyarrow as pa
import pyarrow.parquet as pq

from roskinlib.utils import open_compressed
from roskinlib.schemata.avro import PARSE, SEQUENCE

def deduce_schema(filename, examine_records=1000):
    with open_compressed(filename, 'rb') as file_handle:
        reader = fastavro.reader(file_handle)

        # read a batch of records, size examine_records, to figure out what columns to make
        parses_ids = set()
        lineages_ids = set()
        for record in itertools.islice(reader, examine_records):
            if 'parses' in record:
                parses_ids.update(record['parses'].keys())
            if 'lineages' in record:
                lineages_ids.update(record['lineages'].keys())

        schema = pa.schema([pa.field('subject',  pa.string(), nullable=False),
                            pa.field('sample',   pa.string(), nullable=True),
                            pa.field('source',   pa.string(), nullable=False),
                            pa.field('name',     pa.string(), nullable=False),
                            pa.field('sequence', pa.binary(), nullable=False)] +
                           [pa.field('parse_' + p, pa.binary(), nullable=True) for p in parses_ids] +
                           [pa.field('lineage_' + p, pa.string(), nullable=True) for p in lineages_ids])

        return schema, parses_ids, lineages_ids

def avro_1st_field_iterator(filename, fieldname):
    with open_compressed(filename, 'rb') as file_handle:
        reader = fastavro.reader(file_handle)
        for record in reader:
            yield record[fieldname]

def avro_2nd_field_iterator(filename, fieldname1, fieldname2):
    with open_compressed(filename, 'rb') as file_handle:
        reader = fastavro.reader(file_handle)
        for record in reader:
            yield record[fieldname1][fieldname2]

def avro_2nd_field_missable_iterator(filename, fieldname1, fieldname2):
    with open_compressed(filename, 'rb') as file_handle:
        reader = fastavro.reader(file_handle)
        for record in reader:
            if fieldname2 in record[fieldname1]:
                yield record[fieldname1][fieldname2]
            else:
                yield None

def avro_encoder(it, schema):
    for i in it:
        if i is None:
            yield None
        else:
            data = io.BytesIO()
            fastavro.schemaless_writer(data, schema, i)
            yield data.getvalue()

def take(n, iterable):
    return list(itertools.islice(iterable, n))

def main():
    parser = argparse.ArgumentParser(description='convert a sequence records in Avro file format to Paquet',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('seq_record_filename', metavar='seq_record.avro', help='the Avro file with the sequence records')
    # options
    parser.add_argument('--batch-size', '-b', metavar='B', type=int, default=100000, help='the number of rows to insert at a time')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    filename = args.seq_record_filename
    batch_n = args.batch_size

    sequence_avro_schema = fastavro.parse_schema(SEQUENCE)
    parse_avro_schema    = fastavro.parse_schema(PARSE)

    parquet_schema, parses_ids, lineages_ids = deduce_schema(filename)

    data_iters = [avro_1st_field_iterator(filename, 'subject'),
                  avro_1st_field_iterator(filename, 'sample'),
                  avro_1st_field_iterator(filename, 'source'),
                  avro_1st_field_iterator(filename, 'name'),
                  avro_encoder(avro_1st_field_iterator(filename, 'sequence'), sequence_avro_schema)] + \
                 [avro_encoder(avro_2nd_field_iterator(filename, 'parses', p), parse_avro_schema) for p in parses_ids] + \
                 [avro_2nd_field_missable_iterator(filename, 'lineages', l) for l in lineages_ids]

    #parquet_file = pq.ParquetWriter('example.parquet', parquet_schema, compression='gzip')

    tables_written = 0
    still_data = True
    while still_data:
        data = [take(batch_n, i) for i in data_iters]
        table = pa.Table.from_arrays(data, schema=parquet_schema)

        if table.num_rows == 0:
            still_data = False
        else:
            #parquet_file.write_table(table)
            pq.write_to_dataset(table, root_path='dataset_name', partition_cols=['subject', 'sample', 'source'], compression='gzip')
            tables_written += 1

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
