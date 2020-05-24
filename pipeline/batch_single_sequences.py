#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import os
import gzip

from Bio import SeqIO
from roskinlib.utils import open_compressed, batches


def parse_chain(filenames, file_format, mode='rt'):
    for filename in filenames:
        with open_compressed(filename, mode) as handle:
            for record in SeqIO.parse(handle, file_format):
                yield record

def main():
    parser = argparse.ArgumentParser(description='batch sequences into files with at most a given number of sequences',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # directory to store the batches in
    parser.add_argument('batch_dirname', metavar='dir', help='name for the batch directory')
    # input files
    parser.add_argument('seq_filenames', metavar='seq_file', nargs='+', help='the file with the read 2 sequences')
    # parameters
    parser.add_argument('--input-format',  '-f', metavar='F', default='fasta', help='input file format')
    parser.add_argument('--output-format', '-F', metavar='F', default='fasta', help='output file format')
    parser.add_argument('--batch-size', '-b', metavar='B', type=int, default=50000,
            help='the number of sequences per batch')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    # check if the batch directory already exists
    if os.path.exists(args.batch_dirname):
        logging.error('batch direcotry %s already exists', args.batch_dirname)
        return 10
    else:
        os.mkdir(args.batch_dirname)

    read_count = 0
    batch_count = 0

    for batch in batches(parse_chain(args.seq_filenames, args.input_format), args.batch_size):
        # filename prefix for the batches
        batch_filename = os.path.join(args.batch_dirname, 'batch%06d.fasta' % batch_count)

        logging.info('creating batch %06d', batch_count)

        # compressed batch outout files
        with open(batch_filename, 'wt') as out_handle:
            SeqIO.write(batch, out_handle, args.output_format)
            read_count += len(batch)
        
        batch_count += 1

    logging.info('processed %d read pairs', read_count)
    logging.info('created %d batches', batch_count)
    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))

if __name__ == '__main__':
    sys.exit(main())
