#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import os

import fastavro
from Bio.Seq import Seq
from roskinlib.utils import batches
from roskinlib.seq_rec import best_vdj_score, get_query_region, remove_allele
from roskinlib.warehouse import DirectoryWarehouse

def main():
    parser = argparse.ArgumentParser(description='batch paired-end sequences from an Illumina run of an amplicon library',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # directory to store the batches in
    parser.add_argument('batch_dirname', metavar='dir', help='name for the batch directory')
    # which parse to use
    parser.add_argument('parse_ident', metavar='parse_id', help='the parse identifier to use for splitting the data')
    # lineage label
    parser.add_argument('lineage_ident', metavar='lineage_id', help='the labels to use for lineage structure')
    # input files
    parser.add_argument('seq_record_avro_filenames', metavar='seq_rec.avro', nargs='+', help='avro file with the sequence records for one subject')
    # the maximum number of identical sequences to merge into one entry
    parser.add_argument('--max-idents', '-m', metavar='N', default=50, help='the maximum number of identical sequences to merge into one entry')
    # the minimum CDR3 length
    parser.add_argument('--min-cdr3-len', '-l', metavar='N', type=int, default=10, help='the mimimum CDR3 length (nt)')
    # default cutoffs for V- and J-scores
    parser.add_argument('--min-v-score', '-v', metavar='S',  type=int, default=70, help='minimum V-segment score')
    parser.add_argument('--min-j-score', '-j', metavar='S',  type=int, default=26, help='minimum J-segment score')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    warehouse = DirectoryWarehouse(args.batch_dirname, 'v_segment', 'j_segment', 'cdr3_len', 'subject',
        value_encoder=lambda x: str(x).replace('/', 's'))

    read_count = 0
    unparsed_count = 0
    no_cdr3_count = 0

    parse_ident = args.parse_ident
    lineage_ident = args.lineage_ident

    first_record = True
    data = {}

    for filename in args.seq_record_avro_filenames:
        logging.info('processing reads from %s', filename)
        with open(filename, 'rb') as avro_file_handle:
            for record in fastavro.reader(avro_file_handle):
                read_count += 1

                read_ident = record['name']

                # make sure there is only one subject in the file
                if first_record:
                    subject = record['subject']
                    logging.info('processing reads for subject %s', subject)
                    first_record = False
                else:
                    if subject != record['subject']:
                        logging.error('Avro file must contrain records from a single subject, found %s and %s', subject, record['subject'])
                        sys.exit(10)

                if parse_ident   not in record['parses']   or record['parses'][parse_ident]     is None or \
                   lineage_ident not in record['lineages'] or record['lineages'][lineage_ident] is None:
                    unparsed_count += 1 # no parse, or no hit of the given parse id
                else:
                    read    = record['name']
                    parse   = record['parses'][parse_ident]
                    lineage = record['lineages'][lineage_ident]

                    if parse['has_stop_codon'] is True or parse['v_j_in_frame'] is False:
                        continue

                    best_v, best_v_score, _, _, best_j, best_j_score = best_vdj_score(parse)
                    best_v = remove_allele(best_v)
                    best_j = remove_allele(best_j)

                    # apply the V- and J-score cutoffs
                    if best_v_score is None            or best_j_score is None or \
                       best_v_score < args.min_v_score or best_j_score < args.min_j_score:
                        unparsed_count += 1
                    else:
                        if 'CDR3' not in parse['ranges']:
                            no_cdr3_count += 1
                        else:
                            cdr3_sequence = get_query_region(parse, 'CDR3')
                            cdr3_length   = len(cdr3_sequence)
                            cdr3_aa       = str(Seq(cdr3_sequence).translate())

                            signature = (best_v, best_j, cdr3_length)

                            if signature not in data:
                                data[signature] = {}
                            if cdr3_aa not in data[signature]:
                                data[signature][cdr3_aa] = []
                            data[signature][cdr3_aa].append((subject, lineage, read))

                if read_count % 50000 == 0:
                    logging.info('processed %10d sequence records', read_count)

    logging.info('making batch files')

    for signature, cdr3_aa in data.items():
        best_v, best_j, cdr3_length = signature

        with warehouse.open('.fasta', 'wt', v_segment=best_v, j_segment=best_j, cdr3_len=cdr3_length,
                subject=subject) as fasta_file_handle:
            for sequence, labels in cdr3_aa.items():
                for l in batches(labels, args.max_idents):
                    fasta_file_handle.write('>%s\n%s\n' % (','.join([';'.join(i) for i in l]), sequence))

    logging.info('processed %s sequence records', read_count)
    logging.info('    %d records had no parse or poor V- and J-scores', unparsed_count)
    logging.info('    %d records had no CDR3 region', no_cdr3_count)
    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))

if __name__ == '__main__':
    sys.exit(main())
