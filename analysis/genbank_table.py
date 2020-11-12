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
    best_v_name  = None
    best_v_score = None
    best_d_name  = None
    best_d_score = None
    best_j_name  = None
    best_j_score = None

    if parse is not None:
        for a in parse['alignments']:
            if a['type'] == 'V':
                if best_v_score is None:
                    best_v_name = a['name']
                    best_v_score = a['score']
            elif a['type'] == 'D':
                if best_d_score is None:
                    best_d_name = a['name']
                    best_d_score = a['score']
            elif a['type'] == 'J':
                if best_j_score is None:
                    best_j_name = a['name']
                    best_j_score = a['score']

    return best_v_name, best_v_score, \
           best_d_name, best_d_score, \
           best_j_name, best_j_score


def main():
    parser = argparse.ArgumentParser(description='',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('parse_label', metavar='label', help='the parse label to use for the parse')
    parser.add_argument('filenames', metavar='file', nargs='+', help='the Avro file to read')
    args = parser.parse_args()

    print('accession', 'description', 'v_name', 'd_name', 'j_name', sep='\t')

    for filename in args.filenames:
        with open_compressed(filename, 'rb') as read_handle:
            reader = fastavro.reader(read_handle)

            for record in reader:
                name = record['name']
                assert name.startswith('genbank:')
                accession = name.split(':')[1]

                parse = record['parses'][args.parse_label]
                v_name, _, d_name, _, j_name, _ = best_vdj_score(parse)
                description = None
                if 'description' in record['sequence']['annotations']:
                    description = record['sequence']['annotations']['description']

                print(accession, description, v_name, d_name, j_name, sep='\t')


if __name__ == '__main__':
    sys.exit(main())
