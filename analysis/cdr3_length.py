#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import csv

import fastavro
from collections import defaultdict

import roskinlib
from roskinlib.utils import open_compressed

def best_vdj_score(parse):
    best_v_score = None
    best_d_score = None
    best_j_score = None

    if parse is not None:
        for a in parse['alignments']:
            if a['type'] == 'V':
                if best_v_score is None:
                    best_v_score = a['score']
            elif a['type'] == 'D':
                if best_d_score is None:
                    best_d_score = a['score']
            elif a['type'] == 'J':
                if best_j_score is None:
                    best_j_score = a['score']

    return best_v_score, best_d_score, best_j_score

def get_parse_query(parse):
    if parse is None:
        return None
    else:
        alignment = parse['alignments'][0]
        assert alignment['type'] == 'Q'
        return alignment['alignment']

def make_slice(range_):
    return slice(range_['start'], range_['stop'])

def calc_type(record):
    type_ = record['sequence']['annotations']['target1']
    vh, framework = record['sequence']['annotations']['target2'].split('_')
    if type_ == 'IGHJ'
        return 'DNA-' + framework
    else
        return type_

def main():
    parser = argparse.ArgumentParser(description='get the CDR3 length from an Avro file',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('parse_label', metavar='label', help='the parse label to use for the parse')
    parser.add_argument('filenames', metavar='file', nargs='+', help='the Avro file to read')
    parser.add_argument('--lineage',     '-l', metavar='L', help='the lineage label to use')
    parser.add_argument('--min-v-score', '-v', metavar='S', default=70, help='minimum V-segment score')
    parser.add_argument('--min-j-score', '-j', metavar='S', default=26, help='minimum J-segment score')
    args = parser.parse_args()

    writer = None

    for filename in args.filenames:
        with open_compressed(filename, 'rb') as read_handle:
            reader = fastavro.reader(read_handle)

            for record in reader:
                parse = record['parses'][args.parse_label]
                v_score, _, j_score = best_vdj_score(parse)

                if v_score is not None and j_score is not None and \
                        v_score >= args.min_v_score and j_score >= args.min_j_score:

                    if 'CDR3' in parse['ranges']:
                        subject = record['subject']
                        type_ = record['sequence']['annotations']['target1']

                        v_j_in_frame = parse['v_j_in_frame']
                        has_stop_codon = parse['has_stop_codon']

                        cdr3_slice = make_slice(parse['ranges']['CDR3'])
                        query_sequence = get_parse_query(parse)
                        cdr3_sequence = query_sequence[cdr3_slice]
                        cdr3_length = len(cdr3_sequence.replace('-', ''))

                        if writer is None:
                            if args.lineage:
                                writer = csv.DictWriter(sys.stdout, fieldnames=['subject', 'source', 'type', 'lineage', 'v_j_in_frame', 'has_stop_codon', 'cdr3_length'])
                            else:
                                writer = csv.DictWriter(sys.stdout, fieldnames=['subject', 'source', 'type',            'v_j_in_frame', 'has_stop_codon', 'cdr3_length'])
                            writer.writeheader()

                        row = {'subject': record['subject'], 'source': record['source'],
                               'type': type_, 'v_j_in_frame': v_j_in_frame, 'has_stop_codon': has_stop_codon,
                               'cdr3_length': cdr3_length}
                        if args.lineage:
                            if args.lineage in record['lineages']:
                                row['lineage'] = record['lineages'][args.lineage]

                        writer.writerow(row)

if __name__ == '__main__':
    sys.exit(main())
