#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import csv

from roskinlib.utils import open_compressed

def main():
    parser = argparse.ArgumentParser(description='generate barcode and primer informations for FASTQ read pais', 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # what to put into the source field
    parser.add_argument('source', metavar='source', help='what to put into the source field')
    # the bacode map
    parser.add_argument('barcode_map_filename',  metavar='barcode_map.csv', help='CSV file with the barcode map')
    # file with the barcodes and targeting
    parser.add_argument('barcodes_targets_filename', metavar='idents.csv', help='CSV file with the barcodes and targets')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    logging.info('loading barcode map')
    barcode_map = {}
    with open(args.barcode_map_filename, 'r') as map_handle:
        for row in csv.DictReader(map_handle):
            assert args.source == row['run_label']
            key = (row['barcode1'], row['target1'], row['barcode2'], row['target2'])
            assert key not in barcode_map # make sure there are no duplcate rows
            barcode_map[key] = (row['participant_label'], row['replicate_label'])
    logging.info('loaded %d entries', len(barcode_map))

    demuxing_template = {'pair_id': None,
                         'source': args.source,
                         'subject': None,
                         'sample': None}
    writer = csv.DictWriter(sys.stdout, fieldnames=demuxing_template.keys())
    writer.writeheader()

    logging.info('annotating reads')
    read_pair_count = 0
    annotated_pair_count = 0
    with open_compressed(args.barcodes_targets_filename, 'rt') as barcode_targets_handle:
        for record in csv.DictReader(barcode_targets_handle):
            read_pair_count += 1

            demuxing = demuxing_template.copy()
            demuxing['pair_id'] = record['pair_id']

            # form the lookup
            key = (record['barcode1:name'], record['target1:name'], record['barcode2:name'], record['target2:name'])
            if key in barcode_map:  # if found, annotated with subject, sample
                annotated_pair_count += 1

                particiapant, sample = barcode_map[key]
                demuxing['subject'] = particiapant
                demuxing['sample']  = sample

            writer.writerow(demuxing)

    logging.info('processed %d read pairs', read_pair_count)
    logging.info('annotated %d (%f%%) read pairs', annotated_pair_count, 100.0*annotated_pair_count/read_pair_count)

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
