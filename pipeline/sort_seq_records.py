#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import os
import tempfile
from operator import itemgetter

import fastavro
from fastavro.io.binary_encoder import BinaryEncoder
from fastavro.io.json_encoder import AvroJSONEncoder
from fastavro.read import SYNC_SIZE
from fastavro.write import Writer

from roskinlib.utils import open_compressed

def open_avro(fo, schema, codec='null', sync_interval=1000 * SYNC_SIZE, metadata=None,
              validator=None, sync_marker=None, codec_compression_level=None):
    if isinstance(fo, AvroJSONEncoder):
        writer_class = JSONWriter
    else:
        # Assume a binary IO if an encoder isn't given
        writer_class = Writer
        fo = BinaryEncoder(fo)

    output = writer_class(fo,
                          schema,
                          codec,
                          sync_interval,
                          metadata,
                          validator,
                          sync_marker,
                          codec_compression_level)
    return output

def main():
    parser = argparse.ArgumentParser(description='sort the sequence records in the given Avro file into a HIVE style directory structure',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('pathname_base', metavar='dir_path', help='the base pathname for the HIVE style directory structure')
    parser.add_argument('seq_record_filenames', metavar='seq_rec.avro', nargs='+', help='the Avro file with the sequence records')
    # options
    arg_group = parser.add_mutually_exclusive_group(required=False)
    arg_group.add_argument('--no-none', action='store_true', help='do not process records without a subject')
    arg_group.add_argument('--only-none', action='store_true', help='only process records without a subject')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    # make the base directory if it doesn't already exist
    base_path = args.pathname_base
    logging.info('making base directory %s', base_path)
    try:
        os.mkdir(base_path)
    except FileExistsError:
        logging.info('base directory already exists, adding to it')
    
    # load the records in and group them by subject and source into a list
    with tempfile.TemporaryDirectory() as temp_dir_name:
        logging.info('writing sequences to %s', temp_dir_name)
        temp_handles = {}
        temp_writers = {}
        for filename in args.seq_record_filenames:
            logging.info('loading sequence records from %s', filename)
            with open_compressed(filename, 'rb') as seq_record_handle:
                seq_record_reader = fastavro.reader(seq_record_handle)
                for record in seq_record_reader:
                    subject = record['subject']
                    source  = record['source']
                    
                    if args.no_none and source is None:
                        continue
                    elif args.only_none and source is not None:
                        continue

                    if subject not in temp_handles:
                        temp_handles[subject] = {}
                        temp_writers[subject] = {}
                    if source not in temp_handles[subject]:
                        temp_handles[subject][source] = open(os.path.join(temp_dir_name, f'subject={subject},source={source}.avro'), 'wb')
                        temp_writers[subject][source] = open_avro(temp_handles[subject][source], seq_record_reader.writer_schema)
                    temp_writers[subject][source].write(record)

        # flush and close writers and handles
        for subject in temp_handles:
            for source in temp_handles[subject]:
                temp_writers[subject][source].flush()
                temp_handles[subject][source].close()
        del temp_writers
        
        logging.info('writing output')

        #
        for subject in temp_handles:
            subject_path = os.path.join(base_path, f'subject={subject}')
            # make sure the subject directory is create
            if os.path.isdir(subject_path):
                logging.info('using existing subject directory %s and adding to it', subject_path)
            else:
                logging.info('making subject directory %s', subject_path)
                os.mkdir(subject_path)

            # for each (subject, source)
            for source in temp_handles[subject]:
                logging.info('loading and sorting records subject=%s/source=%s', subject, source)
                with open(os.path.join(temp_dir_name, f'subject={subject},source={source}.avro'), 'rb') as input_handle:
                    reader = fastavro.reader(input_handle)
                    records = list(reader)
                records.sort(key=itemgetter('name'))

                logging.info('writing records subject=%s/source=%s', subject, source)
                output_filename = os.path.join(base_path, f'subject={subject}', f'source={source}.avro')
                with open(output_filename, 'wb') as output_handle:
                    fastavro.writer(output_handle, reader.writer_schema, records, codec='bzip2')
                del records

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
