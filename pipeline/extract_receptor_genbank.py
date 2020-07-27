#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
from collections import defaultdict

from Bio import SeqIO

from roskinlib.utils import open_compressed
from roskinlib.parsers.igblast import IgBLASTParser


def igblast_parse_chain(filenames):
    for filename in filenames:
        with open_compressed(filename, 'rt') as igblast_handle:
            igblast_parse_reader = IgBLASTParser(igblast_handle)
            for parse in igblast_parse_reader:
                yield parse
    
def main():
    parser = argparse.ArgumentParser(description='extract immune receptor sequences from Genbank records',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input files
    parser.add_argument('genbank_filename', metavar='genbank-file', help='the file with the Genbank records')
    parser.add_argument('igblast_output_filenames', metavar='parse.igblast', nargs='+', help='the output of IgBLAST to get the scores from')
    # options
    parser.add_argument('--min-v-score', metavar='S', type=float, default=70.0, help='the minimum score for the V-segment')
    parser.add_argument('--min-j-score', metavar='S', type=float, default=26.0, help='the minimum score for the V-segment')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    min_v_score = args.min_v_score
    min_j_score = args.min_j_score

    with open_compressed(args.genbank_filename, 'rt') as genbank_handle:
        for genbank_record, igblast_record in zip(SeqIO.parse(genbank_handle, 'genbank'),
                                                  igblast_parse_chain(args.igblast_output_filenames)):
            assert genbank_record.id == igblast_record.query_name.split(' ')[0]

            if igblast_record:
                # get the best scores
                best_scores = defaultdict(float)
                for align_line in igblast_record.alignment_lines[1:]:
                    segment_type = align_line.segment_type
                    align_score = igblast_record.significant_alignments[align_line.name]
                    # save the best score for each segment type
                    best_scores[segment_type] = max(best_scores[segment_type], align_score.bit_score)

                if best_scores['V'] >= min_v_score and best_scores['J'] >= min_j_score:
                    SeqIO.write(genbank_record, sys.stdout, 'genbank')

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
