#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import csv

from roskinlib.utils import open_compressed


def basic_sam_parser_match(sam_file_handle):
    prev_read_ident = None
    prev_read_score = None
    for line in sam_file_handle:
        if line.startswith('@'):    # skip header line
            continue
        rows = line.split('\t')
        pair_ident = rows[0]
        for tag in rows[11:]:
            if tag.startswith('AS:i:'):
                score = int(tag[5:])
                break
        else:
            assert False, f'no score found for {pair_ident}'
        if prev_read_ident == pair_ident:
            score = max(score, prev_read_score)
        else:
            prev_read_ident = pair_ident
            prev_read_score = score

            yield pair_ident, score

def main():
    parser = argparse.ArgumentParser(description='extract the read names and alignment scores from a SAM file',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument('sam_filenames', metavar='file.sam', nargs='*', default=['-'], help='the SAM files to process')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    record_template = {'pair_id': None, 'align_score': None}
    writer = csv.DictWriter(sys.stdout, fieldnames=record_template.keys())
    writer.writeheader()

    for sam_filename in args.sam_filenames:
        with open_compressed(sam_filename, 'rt') as sam_file_handle:
            for ident, score in basic_sam_parser_match(sam_file_handle):
                record = record_template.copy()
                record['pair_id'] = ident
                record['align_score'] = score
                writer.writerow(record)

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
