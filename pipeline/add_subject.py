#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time

import fastavro

from roskinlib.utils import open_compressed

def subject_adder(records, subject):
    for record in records:
        record['subject'] = subject
        yield record

def main():
    parser = argparse.ArgumentParser(description='add the given subject to an Avro file',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('seq_record_filename', metavar='seq_record.avro', help='the Avro file with the sequence records')
    parser.add_argument('subject', metavar='S', help='the subject to set')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    with open_compressed(args.seq_record_filename, 'rb') as seq_record_handle:
        seq_record_reader = fastavro.reader(seq_record_handle)

        fastavro.writer(sys.stdout.buffer, seq_record_reader.writer_schema,
                subject_adder(seq_record_reader, args.subject), codec='bzip2')

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
