#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import csv

from itertools import dropwhile
from Bio.SeqIO.QualityIO import FastqGeneralIterator
from fastavro import parse_schema
from fastavro import writer

from roskinlib.utils import open_compressed
from roskinlib.schemata.avro import SEQUENCE_RECORD


def next_with_match(it, match_value, key_column='pair_id'):
    record = next(it)
    while record[key_column] != match_value:
        record = next(it)
    return record

def empty_to_none(x):
    if x == '':
        return None
    else:
        return x

def gather_to_record(merged_read_iter, ident_iter, demux_iter, phix1_iter, phix2_iter):
    for merged_read_id, merged_read_seq, merged_read_qual in merged_read_iter:
        # extract the read pair id
        read_pair_id, read_number = merged_read_id.split(' ')
        assert read_number == '2:N:0:1' # currently, reads should be merged in reverse

        ident_record = next_with_match(ident_iter, read_pair_id)
        demux_record = next_with_match(demux_iter, read_pair_id)
        phix1_record = next_with_match(phix1_iter, read_pair_id)
        phix2_record = next_with_match(phix2_iter, read_pair_id)

        sequence_length = len(merged_read_seq)

        # form the sequence objects with annotations
        sequence = {'sequence': merged_read_seq,
                    'qual':     merged_read_qual,
                    'annotations': {
                        'phix1':    int(phix1_record['align_score']),
                        'barcode1': empty_to_none(ident_record['barcode1:name']),
                        'target1':  empty_to_none(ident_record['target1:name']),
                        'phix2':    int(phix2_record['align_score']),
                        'barcode2': empty_to_none(ident_record['barcode2:name']),
                        'target2':  empty_to_none(ident_record['target2:name'])
                    },
                    'ranges': {}
                   }
        # added in the ranges
        for field in ['random1', 'barcode1', 'target1', 'barcode2', 'target2']:
            if ident_record[field + ':start'] != '':
                assert ident_record[field + ':stop'] != ''
                start = int(ident_record[field + ':start'])
                stop  = int(ident_record[field + ':stop'])
                if field.endswith('1'):
                    start, stop = sequence_length - stop, sequence_length - start
                elif field.endswith('2'):
                    pass
                else:
                    assert False

                sequence['ranges'][field] = {'start': start, 'stop':  stop}

        record = {'name': read_pair_id,
                  'source': empty_to_none(demux_record['source']),
                  'subject': empty_to_none(demux_record['subject']),
                  'sample': empty_to_none(demux_record['sample']),
                  'sequence': sequence,
                  'parses': {},
                  'lineages': {}
                 }

        yield record

def main():
    parser = argparse.ArgumentParser(description='generate barcode and primer informations for FASTQ read pais', 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # 
    parser.add_argument('merged_fastq_filename', metavar='merged.fq', help='the merged reads in FASTQ format')
    parser.add_argument('ident_filename', metavar='idents.csv', help='the list of read idents')
    parser.add_argument('demux_filename', metavar='demux.csv', help='the assigments of reads to subject/sample')
    parser.add_argument('phix1_filename', metavar='phix1.csv', help='file with the alignments of R1 to the PhiX genone')
    parser.add_argument('phix2_filename', metavar='phix2.csv', help='file with the alignments of R2 to the PhiX genone')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    output_schema = parse_schema(SEQUENCE_RECORD)

    # read the FASTQ files
    with open_compressed(args.merged_fastq_filename, 'rt') as merged_read_handle, \
         open_compressed(args.ident_filename, 'rt')        as ident_handle, \
         open_compressed(args.demux_filename, 'rt')        as demux_handle, \
         open_compressed(args.phix1_filename, 'rt')        as phix1_handle, \
         open_compressed(args.phix2_filename, 'rt')        as phix2_handle:

        # the master list of merged reads
        merged_read_iter = FastqGeneralIterator(merged_read_handle)

        ident_iter = csv.DictReader(ident_handle)
        demux_iter = csv.DictReader(demux_handle)
        phix1_iter = csv.DictReader(phix1_handle)
        phix2_iter = csv.DictReader(phix2_handle)

        gatherer = gather_to_record(merged_read_iter, ident_iter, demux_iter, phix1_iter, phix2_iter)

        writer(sys.stdout.buffer, output_schema, gatherer, codec='bzip2')

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
