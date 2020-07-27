#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import re
from collections import Counter

import fastavro

from roskinlib.utils import open_compressed


def main():
    parser = argparse.ArgumentParser(description='get the counts of subject and sources from sequence records objects',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('seq_record_filename', metavar='seq_record.avro', nargs='*', help='the Avro file with the sequence records')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    subject_source_counts = Counter()

    if len(args.seq_record_filename) == 0:
        seq_record_filenames = ['-']
    else:
        seq_record_filenames = args.seq_record_filename

    for record_filename in seq_record_filenames:
        logging.info('processing file %s', record_filename)
        with open_compressed(record_filename, 'rb') as seq_record_handle:
            for record in fastavro.reader(seq_record_handle):
                subject = record['subject']
                source  = record['source']
                subject_source_counts[(subject, source)] += 1

    for subject, source in subject_source_counts:
        print(subject, source, subject_source_counts[(subject, source)], sep='\t')
    
if __name__ == '__main__':
    sys.exit(main())
