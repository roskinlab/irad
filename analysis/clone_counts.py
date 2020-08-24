#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import csv

import fastavro
from collections import defaultdict

import roskinlib
from roskinlib.utils import open_compressed


def main():
    parser = argparse.ArgumentParser(description='get the clone counts in the given Avro files',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('lineage_label', metavar='label', help='the clone label to use')
    parser.add_argument('filenames', metavar='file', nargs='+', help='the Avro files to read')
    args = parser.parse_args()

    clones_counts = defaultdict(int)

    for filename in args.filenames:
        with open_compressed(filename, 'rb') as read_handle:
            reader = fastavro.reader(read_handle)

            for record in reader:
                if args.lineage_label in record['lineages']:
                    subject = record['subject']
                    source = record['source']
                    type_ = record['sequence']['annotations']['target1']
                    lineage = record['lineages'][args.lineage_label]

                    clones_counts[(subject, source, type_, lineage)] += 1

    writer = csv.DictWriter(sys.stdout, fieldnames=['subject', 'source', 'type', 'lineage', 'read_count'])
    writer.writeheader()

    for (subject, source, type_, lineage), read_count in clones_counts.items():
        row = {'subject': subject,
               'source': source,
               'type': type_,
               'lineage': lineage,
               'read_count': read_count}
        writer.writerow(row)

if __name__ == '__main__':
    sys.exit(main())
