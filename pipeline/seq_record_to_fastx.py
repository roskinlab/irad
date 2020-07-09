#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import itertools
import io

import fastavro

from roskinlib.utils import open_compressed

def main():
    parser = argparse.ArgumentParser(description='convert a sequence records in Avro file format to FASTA or FASTQ')
    # input files
    parser.add_argument('seq_record_filenames', metavar='seq_record.avro', nargs='+', help='the Avro file with the sequence records')
    # options
    output_format = parser.add_mutually_exclusive_group()
    output_format.add_argument('--fasta', '-a', default=True, action='store_true', help='output a FASTA file')
    output_format.add_argument('--fastq', '-q', action='store_false', dest='fasta', help='output a FASTQ file')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    for input_filename in args.seq_record_filenames:
        with open_compressed(input_filename, 'rb') as seq_record_handle:
            seq_record_reader = fastavro.reader(seq_record_handle)

            for record in seq_record_reader:
                if args.fasta:
                    print('>%s\n%s' % (record['name'], record['sequence']['sequence']))
                else:
                    print('@%s\n%s\n+\n%s' % (record['name'], record['sequence']['sequence'], record['sequence']['qual']))

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
