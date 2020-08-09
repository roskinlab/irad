#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import csv

from roskinlib.utils import open_compressed

def main():
    parser = argparse.ArgumentParser(description='generate barcode and primer informations for FASTQ read pairs', 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # what to put into the source field
    parser.add_argument('source', metavar='source', help='what to put into the source field')
    # the bacode map
    parser.add_argument('barcode_map_filename',  metavar='barcode_map.csv', help='CSV file with the barcode map')
    # file with the barcodes and targeting
    parser.add_argument('barcodes_targets_filenames', metavar='idents.csv', nargs='+', help='CSV file with the barcodes and targets')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    logging.info('loading barcode map')
    barcode_map = {}
    with open(args.barcode_map_filename, 'r') as map_handle:
        for row in csv.DictReader(map_handle):
            assert args.source == row['run_label']
            key = (row['barcode1'], row['target1'], row['barcode2'], row['target2'])
            assert key not in barcode_map # make sure there are no duplcate rows
            barcode_map[key] = (row['participant_label'], row['replicate_label'])
    logging.info('loaded %d entries', len(barcode_map))

    for barcodes_targets_filename in args.barcodes_targets_filenames:
        logging.info('processing file %s', barcodes_targets_filename)
        with open_compressed(barcodes_targets_filename, 'rt') as barcode_targets_handle:
            for record in csv.DictReader(barcode_targets_handle):
                key = (record['barcode1:name'], record['target1:name'], record['barcode2:name'], record['target2:name'])
                if key not in barcode_map:  # if found, annotated with subject, sample
                    print(*key, sep=',')

if __name__ == '__main__':
    sys.exit(main())
