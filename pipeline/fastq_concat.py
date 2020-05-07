#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse

from Bio.SeqIO.QualityIO import FastqGeneralIterator
from Bio.Seq import _dna_complement_table

from roskinlib.utils import open_compressed


def main():
    parser = argparse.ArgumentParser(description='concatinate two FASTQ files, rc\'ing the second one, with a given spacer in between',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input file
    parser.add_argument('fastq1_filename', metavar='file1.fq', help='the R1 FASTQ file')
    parser.add_argument('fastq2_filename', metavar='file2.fq', help='the R2 FASTQ file to reverse complement and concatinate to the above')
    # options
    parser.add_argument('--spacer',      '-s', type=str, default='XXXXXXXX', help='the spacer sequence')
    parser.add_argument('--qual-spacer', '-q', type=int, default=0, help='the qual score to assign to the spacer')

    args = parser.parse_args()

    spacer_seq  = args.spacer
    spacer_qual = chr(33 + args.qual_spacer) * len(spacer_seq)

    # read the FASTQ file
    with open_compressed(args.fastq1_filename, 'rt') as input1_handle, \
         open_compressed(args.fastq2_filename, 'rt') as input2_handle:
        for r1, r2 in zip(FastqGeneralIterator(input1_handle), FastqGeneralIterator(input2_handle)):
            r1_id, r1_seq, r1_qual = r1
            r2_id, r2_seq, r2_qual = r2

            r1_seq  += spacer_seq  + r2_seq.translate(_dna_complement_table)[::-1]
            r1_qual += spacer_qual + r2_qual[::-1]

            print('@%s\n%s\n+\n%s' % (r1_id, r1_seq, r1_qual))

if __name__ == '__main__':
    sys.exit(main())
