#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time

from Bio import SeqIO
from fastavro import parse_schema
from fastavro import writer

from roskinlib.utils import open_compressed
from roskinlib.schemata.avro import SEQUENCE_RECORD

def seq_record_from_genbank(genbank_record):
    sequence_annotations = {'organism':    genbank_record.annotations['organism'],
                            'description': genbank_record.description}
    sequence = {'sequence': str(genbank_record.seq),
                'qual': '',
                'annotations': sequence_annotations,
                'ranges': {}}
    return {'name': 'genbank:' + genbank_record.id,
            'source': 'Genbank',
            'subject': None,
            'sample': None,
            'sequence': sequence,
            'parses': {},
            'lineages': {}}

def genbank_filter_chain(filenames, organism=None, max_length=None):
    processed_read_count = 0
    for genbank_filename in filenames:
        logging.info('processing %s', genbank_filename)
        with open_compressed(genbank_filename, 'rt') as genbank_file:
            for record in SeqIO.parse(genbank_file, 'genbank'):
                if (organism is None) or (organism == record.annotations['organism']):
                    sequence_length = len(record.seq)
                    if (max_length is None) or (sequence_length <= max_length):
                        processed_read_count += 1
                        yield seq_record_from_genbank(record)
                    else:
                        logging.info('record %s (%s) is too big, %d > %s, ignoring',
                                record.id, record.description, sequence_length, max_length)

    logging.info('processed %s read pairs', processed_read_count)


def main():
    parser = argparse.ArgumentParser(description='loads Genbank sequences',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # files
    parser.add_argument('genbank_filenames', metavar='genbank_file', nargs='+', help='the file with the Genbank records')
    parser.add_argument('--organism', '-o', metavar='O', help='only process records with the given organism')
    parser.add_argument('--max-length', '-m', metavar='L', type=int, default=50000, help='ignore sequences longer than this')

    # setup schema
    avro_schema = parse_schema(SEQUENCE_RECORD)

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    genbank_records = genbank_filter_chain(args.genbank_filenames, args.organism, args.max_length)
    writer(sys.stdout.buffer, avro_schema, genbank_records, codec='bzip2')

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
