#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import json

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

def main():
    parser = argparse.ArgumentParser(description='get the CDR3 length from an Avro file',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('parse_label', metavar='label', help='the parse label to use for the parse')
    parser.add_argument('filename', metavar='file', help='the Avro file to read')
    parser.add_argument('--min-v-score', '-v', metavar='S', default=70, help='minimum V-segment score')
    parser.add_argument('--min-j-score', '-j', metavar='S', default=26, help='minimum J-segment score')
    args = parser.parse_args()

    reader = fastavro.reader(open_compressed(args.filename, 'rb'))

    subject = None
    cdr3_length_type = defaultdict(list)

    for record in reader:
        parse = record['parses'][args.parse_label]
        v_score, _, j_score = best_vdj_score(parse)

        if v_score is not None and j_score is not None and \
                v_score >= args.min_v_score and j_score >= args.min_j_score:

            if 'CDR3' in parse['ranges']:
                if subject is None:
                    subject = record['subject']
                else:
                    assert subject == record['subject']

                type_ = record['sequence']['annotations']['target1']


                cdr3_slice = make_slice(parse['ranges']['CDR3'])
                query_sequence = get_parse_query(parse)
                cdr3_sequence = query_sequence[cdr3_slice]

                cdr3_length = len(cdr3_sequence.replace('-', ''))

                cdr3_length_type[type_].append(cdr3_length)

    for type_, lengths in cdr3_length_type.items():
        mean_cdr3_length = sum(lengths) / len(lengths)
        print(subject, type_, mean_cdr3_length, sep='\t')

if __name__ == '__main__':
    sys.exit(main())
