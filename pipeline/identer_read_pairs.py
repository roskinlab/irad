#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import csv
from Bio.SeqIO.QualityIO import FastqGeneralIterator

from roskinlib.utils import open_compressed
from roskinlib.matcher import RandomBarcodeTargetMatcher


def load_sequences_labeled(filenames, sep='\t'):
    sequences_labeled = {}
    for filename in filenames:
        for row in open(filename, 'r'):
            ident, sequence = row[:-1].split(sep)
            assert sequence not in sequences_labeled
            sequences_labeled[sequence] = ident
    return sequences_labeled

def main():
    parser = argparse.ArgumentParser(description='generate barcode and primer informations for FASTQ read pais', 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input sequence files
    parser.add_argument('r1_filename', metavar='file_r1.fq', help='the FASTQ file with the read 1 sequences')
    parser.add_argument('r2_filename', metavar='file_r2.fq', help='the FASTQ file with the read 2 sequences')
    # barcodes and trimmer matching parameters for R1
    parser.add_argument('--barcodes1', metavar='bc', nargs='+', required=True, help='file(s) with barcodes to use on read 1')
    parser.add_argument('--targets1',  metavar='tg',  nargs='+', required=True, help='files(s) with the targeting sequences to use on read 1')
    parser.add_argument('--ran-length1',  metavar='N', type=int, default=4, help='the number of random diversity bases on read 1')
    parser.add_argument('--ran-radius1',  metavar='N', type=int, default=1, help='the maximum shift of the random diversity bases on read 1')
    # barcodes and trimmer matching parameters for R2
    parser.add_argument('--targets2',  metavar='tg',  nargs='+', required=True, help='files(s) with the targeting sequences to use on read 2')
    parser.add_argument('--barcodes2', metavar='bc', nargs='+', required=True, help='file(s) with barcodes to use on read 2')
    parser.add_argument('--ran-length2',  metavar='N', type=int, default=0, help='the number of random diversity bases on read 2')
    parser.add_argument('--ran-radius2',  metavar='N', type=int, default=0, help='the maximum shift of the random diversity bases on read 2')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    # load the barcodes
    logging.info('loading barcodes')
    barcodes1_dict = load_sequences_labeled(args.barcodes1)
    barcodes2_dict = load_sequences_labeled(args.barcodes2)

    # load the targeting sequences
    logging.info('loading targeting sequences')
    targets1_dict = load_sequences_labeled(args.targets1)
    targets2_dict = load_sequences_labeled(args.targets2)

    # make the matcher objects
    logging.info('creating read 1 matcher')
    read1_matcher = RandomBarcodeTargetMatcher(args.ran_length1, args.ran_radius1, barcodes1_dict, targets1_dict, target_max_diff=2)
    logging.info('creating read 2 matcher')
    read2_matcher = RandomBarcodeTargetMatcher(args.ran_length2, args.ran_radius2, barcodes2_dict, targets2_dict, target_max_diff=2, allow_collesion=True)

    logging.info('annotating read pairs')

    annotated_read_count = 0

    record_template = {'pair_id':        None,
                       'random1:start':  None, 
                       'random1:stop':   None, 
                       'barcode1:name':  None, 
                       'barcode1:start': None, 
                       'barcode1:stop':  None, 
                       'target1:name':   None, 
                       'target1:start':  None, 
                       'target1:stop':   None, 
                       'barcode2:name':  None, 
                       'barcode2:start': None, 
                       'barcode2:stop':  None, 
                       'target2:name':   None, 
                       'target2:start':  None,
                       'target2:stop':   None}
    writer = csv.DictWriter(sys.stdout, fieldnames=record_template.keys())
    writer.writeheader()

    # read the FASTQ files
    with open_compressed(args.r1_filename, 'rt') as in_read1_handle, \
         open_compressed(args.r2_filename, 'rt') as in_read2_handle:

        # iterate over the read files
        for r1_read, r2_read in zip(FastqGeneralIterator(in_read1_handle),
                                    FastqGeneralIterator(in_read2_handle)):
            # break out the read parts
            r1_id, r1_seq, r1_qual = r1_read
            r2_id, r2_seq, r2_qual = r2_read

            # make sure the read pairs match
            r1_id = r1_id.split(' ')[0]
            r2_id = r2_id.split(' ')[0]
            assert r1_id == r2_id, f'read {r1_id} != {r2_id}'
            
            record = record_template.copy()
            record['pair_id'] = r1_id

            # process read1
            match1 = read1_matcher.match(r1_seq)
            if match1:
                if match1[0] != 0:
                    record['random1:start'] = 0
                    record['random1:stop']  = match1[0]
                record['barcode1:name']     = match1[1]
                record['barcode1:start']    = match1[0]
                record['barcode1:stop']     = match1[0] + match1[2]
                record['target1:name']      = match1[3]
                record['target1:start']     = match1[0] + match1[2]
                record['target1:stop']      = match1[0] + match1[2] + match1[4]

            # process read2
            match2 = read2_matcher.match(r2_seq)
            if match2:
                record['barcode2:name']     = match2[1]
                record['barcode2:start']    = 0
                record['barcode2:stop']     = match2[0] + match2[2]
                record['target2:name']      = match2[3]
                record['target2:start']     = match2[0] + match2[2]
                record['target2:stop']      = match2[0] + match2[2] + match2[4]

            writer.writerow(record)

    logging.info('annotated %d read pairs', annotated_read_count)

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
