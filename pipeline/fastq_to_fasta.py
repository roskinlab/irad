#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse

from Bio.SeqIO.QualityIO import FastqGeneralIterator

from roskinlib.utils import open_compressed


def main():
    parser = argparse.ArgumentParser(description='batch paired-end sequences from an Illumina run of an amplicon library',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input file
    parser.add_argument('fastq_filename', metavar='file.fq', default='-', help='FASTQ file to convert')
    # options
    parser.add_argument('-t', '--trim-label', action='store_true', help='trimmed the read label')

    args = parser.parse_args()

    # read the FASTQ file
    with open_compressed(args.fastq_filename, 'rt') as input_handle:
        for read_id, read_seq, read_qual in FastqGeneralIterator(input_handle):
            if args.trim_label:
                read_id = read_id.split(' ')[0]
            print('>%s\n%s' % (read_id, read_seq))

if __name__ == '__main__':
    sys.exit(main())
