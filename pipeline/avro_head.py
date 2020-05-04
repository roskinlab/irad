#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
from itertools import islice

import fastavro


def main():
    parser = argparse.ArgumentParser(description='output the first part of an Avro file',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('avro_filename', metavar='file.avro', help='the Avro file')
    # options
    parser.add_argument('--records', '-n', metavar='N', type=int, default=10, help='output the first N records instead of the first 10')

    args = parser.parse_args()
    
    with open(args.avro_filename, 'rb') as avro_handle:
        reader = fastavro.reader(avro_handle)
        fastavro.writer(sys.stdout.buffer, reader.writer_schema, islice(reader, args.records), codec='bzip2')

if __name__ == '__main__':
    sys.exit(main())
