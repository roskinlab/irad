#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import os
import gzip

from Bio.SeqIO.QualityIO import FastqGeneralIterator

from roskinlib.utils import open_compressed, batches


def main():
    parser = argparse.ArgumentParser(description='batch paired-end sequences from an Illumina run of an amplicon library',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # directory to store the batches in
    parser.add_argument('batch_dirname', metavar='dir', help='name for the batch directory')
    # input files
    parser.add_argument('r1_filename', metavar='r1_file', help='the file with the read 1 sequences')
    parser.add_argument('r2_filename', metavar='r2_file', help='the file with the read 2 sequences')
    # parameters
    parser.add_argument('--batch-size', '-b', metavar='B', type=int, default=50000,
            help='the number of read pairs to insert at a time')

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

    # read the FASTQ files
    with open_compressed(args.r1_filename, 'rt') as in_read1_handle, \
         open_compressed(args.r2_filename, 'rt') as in_read2_handle:
        
        # iterate over the read files
        for r1_batch, r2_batch in zip(batches(FastqGeneralIterator(in_read1_handle), args.batch_size),
                                      batches(FastqGeneralIterator(in_read2_handle), args.batch_size)):
            # filename prefix for the batches
            batch_prefix = os.path.join(args.batch_dirname, 'batch%06d' % batch_count)

            logging.info('creating batch %06d', batch_count)

            # compressed batch outout files
            with gzip.open(batch_prefix + '.fq1.gz', 'wt') as out_read1_handle, \
                 gzip.open(batch_prefix + '.fq2.gz', 'wt') as out_read2_handle:

                # for each read pair in the batch
                for r1_read, r2_read in zip(r1_batch, r2_batch):
                    r1_id, r1_seq, r1_qual = r1_read
                    r2_id, r2_seq, r2_qual = r2_read

                    # check that the read ids are the same
                    assert r1_id.split(' ')[0] == r2_id.split(' ')[0], 'read ids do not match %s != %s' % (r1_id, r2_id)

                    out_read1_handle.write('@%s\n%s\n+\n%s\n' % (r1_id, r1_seq, r1_qual))
                    out_read2_handle.write('@%s\n%s\n+\n%s\n' % (r2_id, r2_seq, r2_qual))

                    read_count += 1
            
            batch_count += 1

    logging.info('processed %d read pairs', read_count)
    logging.info('created %d batches', batch_count)
    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))

if __name__ == '__main__':
    sys.exit(main())
