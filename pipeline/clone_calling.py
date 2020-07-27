#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import re
from collections import defaultdict

import fastavro
from Bio import SeqIO

from roskinlib.utils import open_compressed

def clone_annotator(clone_calls, seq_record_iter, lineage_label):
    processed_count = 0
    unannotated_count = 0
    for record in seq_record_iter:
        assert lineage_label not in record['lineages']

        processed_count += 1
        if record['name'] in clone_calls:
            record['lineages'][lineage_label] = clone_calls[record['name']]
        else:
            unannotated_count += 1

        yield record

        if processed_count % 50000 == 0:
            logging.info('processed %10d sequence records', processed_count)

    logging.info('processed %d sequence records', processed_count)
    logging.info('    %d (%.4f%%) records were unannotated', unannotated_count, 100.0*unannotated_count/processed_count)


def main():
    parser = argparse.ArgumentParser(description='load clone calling annotations into an Avro sequence record',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('seq_record_filename', metavar='seq_record.avro', help='the Avro file with the sequence records')
    parser.add_argument('lineages_label', metavar='label', help='the labels to use for the clone calling')
    parser.add_argument('cluster_filenames', metavar='seq.clust', nargs='*', help='clustering files')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()
    
    if len(args.cluster_filenames) == 0:
        logging.info('loading cluster files from stdin')
        cluster_filenames = sys.stdin
    else:
        cluster_filenames = args.cluster_filenames

    clone_labels = set()
    clone_calls = {}

    logging.info('loading lineage calls')
    for filename in cluster_filenames:
        filename = filename.rstrip()
        with open(filename, 'rt') as cluster_handle:
            for cluster in cluster_handle:
                representative, members = cluster[:-1].split('\t')
                representative = representative.split(',')[0] # arbitrarily pick first equal as rep
                clone_labels.add(representative)

                for member in members.split(','):
                    clone_calls[member] = representative
    logging.info('loaded %d clones', len(clone_labels))
    logging.info('    that include %d memebers', len(clone_calls))
    logging.info('    average %0.4f members per clone', len(clone_calls) / len(clone_labels))

    logging.info('annotating sequence records')
    with open_compressed(args.seq_record_filename, 'rb') as seq_record_handle:
        seq_record_reader = fastavro.reader(seq_record_handle)

        annotator = clone_annotator(clone_calls, seq_record_reader, args.lineages_label)

        fastavro.writer(sys.stdout.buffer, seq_record_reader.writer_schema, annotator, codec='bzip2')

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
