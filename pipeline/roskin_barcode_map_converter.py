#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import csv


def fix_barcode(b):
    letter = b[0]
    number = int(b[1:])
    return '%s%02d' % (letter, number)

def fix_isotype(s):
    assert s.startswith('Ig')
    return 'IGH' + s[2:]

def main():
    parser = argparse.ArgumentParser(description='convert a barcode map from the Roskin lab into full format',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # the Roskin lab style barcode map
    parser.add_argument('barcode_map_filename', metavar='barcode_map.tsv', help='the barcode map to convert')
    # the source name
    parser.add_argument('source_label', metavar='source', help='the source to label this data')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    header_written = False
    writer = csv.DictWriter(sys.stdout, fieldnames=['run_label', 'participant_label', 'replicate_label',
                                                    'barcode1', 'target1', 'barcode2', 'target2'])

    logging.info('processing barcode map %s', args.barcode_map_filename)
    with open(args.barcode_map_filename, 'rt') as barcode_handle:
        for record in csv.DictReader(barcode_handle, fieldnames=['sample_label', 'forward_barcode_primer', 'reverse_barcode_primer']):
            # split out the parts of the primer
            forward_adapter, forward_barcode = record['forward_barcode_primer'].split('_')
            reverse_adapter, reverse_barcode = record['reverse_barcode_primer'].split('_')

            # build new record
            new_record = {'run_label': args.source_label,
                          'participant_label': 'roskinlab:' + record['sample_label'],
                          'replicate_label': 'roskinlab:' + record['sample_label'],
                          'barcode1': forward_barcode,
                          'barcode2': reverse_barcode}
            # add rows for each pool
            for isotype in ['IGHM', 'IGHD', 'IGHG', 'IGHA', 'IGHE']:
                for v_region in ['VH1_FR1', 'VH2_FR1', 'VH3_FR1', 'VH4_FR1', 'VH5_FR1', 'VH6_FR1']:
                    new_record['target1'] = isotype
                    new_record['target2'] = v_region

                    if not header_written:
                        writer.writeheader()
                        header_written = True
                    writer.writerow(new_record)

if __name__ == '__main__':
    sys.exit(main())
