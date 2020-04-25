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


def get_subjects(seq_record_iter):
    for record in seq_record_iter:
        yield record['subject']

def main():
    parser = argparse.ArgumentParser(description='get the list of subjects in a set of sequence records',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('seq_record_filename', metavar='seq_record.avro', nargs='*', help='the Avro file with the sequence records')
    # options
    parser.add_argument('-s', '--sort-counts', action='store_true', help='sort by per-subject counts')
    parser.add_argument('-c', '--show-counts', action='store_true', help='show the per-subjects counts')
    parser.add_argument('-n', '--show-none', action='store_true', help='show the un-assigned records')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    subject_counts = Counter()

    if len(args.seq_record_filename) == 0:
        seq_record_filenames = ['-']
    else:
        seq_record_filenames = args.seq_record_filename

    for record_filename in seq_record_filenames:
        logging.info('processing file %s', record_filename)
        with open_compressed(record_filename, 'rb') as seq_record_handle:
            subject_counts.update(get_subjects(fastavro.reader(seq_record_handle)))
    
    if args.sort_counts:
        for s, c in subject_counts.most_common():
            if args.show_none or s is not None:
                if args.show_counts:
                    print(s, c, sep='\t')
                else:
                    print(s)
    else:
        for s in sorted(subject_counts.keys(), key=str):
            if args.show_none or s is not None:
                if args.show_counts:
                    c = subject_counts[s]
                    print(s, c, sep='\t')
                else:
                    print(s)
        
if __name__ == '__main__':
    sys.exit(main())
