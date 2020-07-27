#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
from pprint import pprint

from Bio import SeqIO
import fastavro

from roskinlib.utils import open_compressed
from roskinlib import tests

def avro_file_record_filter_iter(filenames, subject):
    for filename in filenames:
        logging.info('processing file %s', filename)
        for record in fastavro.reader(open_compressed(filename, 'rb')):
            if record['subject'] == subject:
                yield record

def main():
    parser = argparse.ArgumentParser(description='validate sequence records from Avro files',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('repertoire_filenames', metavar='repertoire-file', nargs=3, help='the V(D)J repertoire file used in IgBLAST')
    parser.add_argument('sequence_record_filenames', metavar='seq_record.avro', nargs='+', help='Avro files with the sequence records to test')


    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    v_repertoire = {r.id: str(r.seq) for r in SeqIO.parse(args.repertoire_filenames[0], 'fasta')}
    d_repertoire = {r.id: str(r.seq) for r in SeqIO.parse(args.repertoire_filenames[1], 'fasta')}
    j_repertoire = {r.id: str(r.seq) for r in SeqIO.parse(args.repertoire_filenames[2], 'fasta')}

    record_count = 0

    error = False
    for filename in args.sequence_record_filenames:
        logging.info('processing file %s', filename)
        if error:
            break
        with open_compressed(filename, 'rb') as input_handle:
            for record in fastavro.reader(input_handle):
                if not tests.test_parse_alignment_structure(record):
                    pprint(record)
                    error = True
                if not tests.test_parse_alignment_sequences(record, v_repertoire, d_repertoire, j_repertoire):
                    pprint(record)
                    error = True

                if error:
                    break
                
                record_count += 1

    logging.info('processed %d sequence records', record_count)
    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))

if __name__ == '__main__':
    sys.exit(main())
