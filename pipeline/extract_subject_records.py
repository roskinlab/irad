#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import re
import os
from collections import Counter
from itertools import chain

import fastavro

import roskinlib

def avro_file_record_filter_iter(filenames, subject):
    for filename in filenames:
        logging.info('processing file %s', filename)
        for record in fastavro.reader(open_compressed(filename, 'rb')):
            if record['subject'] == subject:
                yield record

def main():
    parser = argparse.ArgumentParser(description='extract sequence records from Avro files with a given subject',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('source_record_filename', metavar='seq_record.avro', nargs='+', help='Avro files with the sequence records to extract')
    parser.add_argument('dest_record_filename', metavar='target.avro', help='the destination Avro file')
    parser.add_argument('subject_label', metavar='subject', help='the subject to extract, use none for un-assigned records')
    # append
    parser.add_argument('-a', '--append', action='store_true', help='append records to an existing Avro file')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    if os.path.exists(args.dest_record_filename):
        if args.append:
            logging.info('appending to existing sequence record file %s', args.dest_record_filename)
        else:
            logging.error('destination file already exists, to append use the --apppend/-a flag to add to it, exiting')
            return 10

    if args.subject_label == 'none':
        args.subject_label = None
    logging.info('extracting records for subject %s', args.subject_label)

    # keep in the first file to get the schema
    with open_compressed(args.source_record_filename[0], 'rb') as seq_record_handle:
        reader = fastavro.reader(open_compressed(args.source_record_filename[0], 'rb'))
        schema = reader.writer_schema

    # open and append to the destination file
    with open_compressed(args.dest_record_filename, 'a+b') as dest_record_handle:
        fastavro.writer(dest_record_handle, schema,
                avro_file_record_filter_iter(args.source_record_filename, args.subject_label), codec='bzip2')

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))

if __name__ == '__main__':
    sys.exit(main())
