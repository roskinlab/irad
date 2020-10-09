#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
from collections import Counter

from Bio import AlignIO, SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord

from roskinlib import seqclust
from roskinlib.warehouse import DirectoryWarehouse

def simple_weighted_consensus(alignment, weight_function=lambda x: 1):
    consensus = []

    # pre-calculate the weigths of the sequences
    sequence_weights = {s.id: weight_function(s) for s in alignment}

    
    # for each column of the alignment
    alignment_width = alignment.get_alignment_length()
    for n in range(alignment_width):
        obv_base_counts = Counter()

        for sequence in alignment:
            if n < len(sequence.seq):
                base = sequence.seq[n]
                if base != '-' and base != '.':
                    obv_base_counts[base] += sequence_weights[sequence.id]

        most_common_base, most_common_count = obv_base_counts.most_common(1)[0]
        consensus.append(most_common_base)

    return Seq(''.join(consensus))


def main(arguments):
    # program options
    parser = argparse.ArgumentParser(description='',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # input data
    parser.add_argument('input_alignment', metavar='align.fasta', help='the input alignment')
    # labels
    parser.add_argument('consensus_id', metavar='id', help='the name of the consensus sequence')
    # options
    parser.add_argument('--format', '-f', metavar='F', default='fasta', help='input alignment format')

    args = parser.parse_args(arguments)
    logging.basicConfig(level=logging.INFO)

    with open(args.input_alignment, 'r') as input_align_handle:
        alignment = AlignIO.read(input_align_handle, args.format)
        consensus = simple_weighted_consensus(alignment, weight_function=lambda x: 1 + x.id.count(','))
        record = SeqRecord(consensus, id=args.consensus_id, description='')
        SeqIO.write(record, sys.stdout, args.format)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
