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
    parser = argparse.ArgumentParser(description='convert a barcode map from the Boydlab into full format',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # table that maps reps. to participants
    parser.add_argument('participant_replicates_table_filename', metavar='part_rep.tsv',
            help='the table of replicates and the subject they come from')
    # the Boyd lab style barcode map
    parser.add_argument('barcode_map_filename', metavar='barcode_map.tsv', help='the barcode map to convert')
    # the source name
    parser.add_argument('source_label', metavar='source', help='the source to label this data')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)

    # load the table that maps replicates to participant labels
    logging.info('loading the table of participants and replicates from %s', args.participant_replicates_table_filename)
    replicate_to_participant = {}
    with open(args.participant_replicates_table_filename, 'rt') as part_rep_handle:
        for record in csv.DictReader(part_rep_handle):
            replicate_to_participant[record['replicate_label']] = record['participant_label']

    header_written = False
    writer = csv.DictWriter(sys.stdout, fieldnames=['run_label', 'participant_label', 'replicate_label',
                                                    'barcode1', 'target1', 'barcode2', 'target2'])

    logging.info('processing barcode map %s', args.barcode_map_filename)
    with open(args.barcode_map_filename, 'rt') as barcode_handle:
        for record in csv.DictReader(barcode_handle, fieldnames=['replicate_label', 'forward_barcode_primer', 'reverse_barcode']):
            # split out the parts of the primer
            if record['forward_barcode_primer'].count('_') == 2:    # cDNA barcodes
                forward_adapter, forward_target, forward_barcode = record['forward_barcode_primer'].split('_')
                forward_target = fix_isotype(forward_target)
            elif record['forward_barcode_primer'].count('_') == 1:  # gDNA barcodes
                forward_target, forward_barcode = record['forward_barcode_primer'].split('_')
                assert forward_target == 'MiSeq'
                forward_target = 'IGHJ'

            reverse_adapter, reverse_barcode = record['reverse_barcode'].split('_')

            # build new record
            new_record = {'run_label': args.source_label,
                          'participant_label': 'boydlab:' + replicate_to_participant[record['replicate_label']],
                          'replicate_label': 'boydlab:' + record['replicate_label'],
                          'barcode1': forward_barcode,
                          'target1': forward_target,
                          'barcode2': reverse_barcode}
            # add rows for each pool
            for v_region in ['VH1_FR1', 'VH2_FR1', 'VH3_FR1', 'VH4_FR1', 'VH5_FR1', 'VH6_FR1']:
                new_record['target2'] = v_region

                if not header_written:
                    writer.writeheader()
                    header_written = True
                writer.writerow(new_record)

if __name__ == '__main__':
    sys.exit(main())
