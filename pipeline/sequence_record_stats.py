#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import re
import os
from collections import Counter
from itertools import chain

import fastavro
from roskinlib.utils import open_compressed


def main():
    parser = argparse.ArgumentParser(description='generate some basic stats from a set of sequence records',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('seq_record_filenames', metavar='seq_record.avro', nargs='+', help='Avro files with the sequence records')
    #
    parser.add_argument('--parse-label', '-p', metavar='L', help='collect stats on the given parse label')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    record_count = 0
    no_subject = 0
    no_subject_full_ident = 0
    no_subject_phix = 0
    no_subject_parsed = 0
    yes_subject = 0
    yes_subject_parsed = 0

    for filename in args.seq_record_filenames:
        logging.info('processing sequence record file %s', filename)
        with open_compressed(filename, 'rb') as input_handle:
            reader = fastavro.reader(input_handle)
            for record in reader:
                record_count += 1

                if record['subject'] is None:
                    no_subject += 1

                    if record['sequence']['annotations']['barcode1'] is not None and \
                       record['sequence']['annotations']['target1']  is not None and \
                       record['sequence']['annotations']['barcode1'] is not None and \
                       record['sequence']['annotations']['target2']  is not None:
                        no_subject_full_ident += 1

                    if record['sequence']['annotations']['phix1'] > 0 or \
                       record['sequence']['annotations']['phix2'] > 0:
                        no_subject_phix += 1

                    if args.parse_label:
                        if args.parse_label in record['parses'] and record['parses'][args.parse_label] is not None:
                            no_subject_parsed += 1
                else:
                    yes_subject += 1
                    if args.parse_label:
                        if args.parse_label in record['parses'] and record['parses'][args.parse_label] is not None:
                            yes_subject_parsed += 1

    print('processed %d records' % record_count)
    print('  %d (%0.2f%%) had subject' % (yes_subject, 100*yes_subject/record_count))
    if args.parse_label:
        print('    %d (%0.2f%%) of those had parses (%s)' % (yes_subject_parsed, 100*yes_subject_parsed/yes_subject, args.parse_label))
    print('  %d (%0.2f%%) had no subject' % (no_subject, 100*no_subject/record_count))
    if args.parse_label:
        print('    %d (%0.2f%%) of those had parses (%s)' % (no_subject_parsed, 100*no_subject_parsed/no_subject, args.parse_label))
    print('    %d (%0.2f%%) of those where PhiX' % (no_subject_phix, 100*no_subject_phix/no_subject))
    print('    %d (%0.2f%%) of those had full idents' % (no_subject_full_ident, 100*no_subject_full_ident/no_subject))

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))

if __name__ == '__main__':
    sys.exit(main())
