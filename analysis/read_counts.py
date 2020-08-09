#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import json

import fastavro
from collections import defaultdict

import roskinlib
from roskinlib.utils import open_compressed


def main():
    parser = argparse.ArgumentParser(description='get the CDR3 length from an Avro file',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('filename', metavar='file', help='the Avro file to read')
    args = parser.parse_args()

    reader = fastavro.reader(open_compressed(args.filename, 'rb'))

    subject = None
    read_counts_type = defaultdict(int)

    for record in reader:
        if subject is None:
            subject = record['subject']
        else:
            assert subject == record['subject']
        type_ = record['sequence']['annotations']['target1']
        read_counts_type[type_] += 1

    for type_, count in read_counts_type.items():
        print(subject, type_, count, sep='\t')

if __name__ == '__main__':
    sys.exit(main())
