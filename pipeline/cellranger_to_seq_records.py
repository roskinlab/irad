#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import logging
import time
import csv

from Bio.SeqIO.QualityIO import FastqGeneralIterator
from fastavro import parse_schema, writer

from roskinlib.utils import open_compressed
from roskinlib.schemata.avro import SEQUENCE_RECORD

def make_seq_records(cell_umis, cell_contigs, sequences, subject=None, sample=None, source=None):
    for cell in cell_umis:
        contig_seq, contig_qual = sequences[cell_contigs[cell]]
        # form the sequence objects with annotations
        sequence = {'sequence': contig_seq,
                    'qual':     contig_qual,
                    'annotations': {
                        'umis': cell_umis[cell]
                    }, 'ranges': {}}

        record = {'name': cell_contigs[cell],
                  'subject': subject,
                  'sample': sample,
                  'source': source,
                  'sequence': sequence,
                  'parses': {},
                  'lineages': {}
                 }
        
        yield record

def main():
    parser = argparse.ArgumentParser(description='generate barcode and primer informations for FASTQ read pais', 
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # paths
    parser.add_argument('cell_ranger_vdj_path', metavar='cellranger_outs_dir', default='.', help='directory with the output of Cell Ranger VDJ pipeline')
    # the source name
    parser.add_argument('--subject', metavar='subject', default=None, help='the subject to label this data')
    parser.add_argument('--sample',  metavar='sample',  default=None, help='the sample to label this data')
    parser.add_argument('--source',  metavar='source',  default=None, help='the source to label this data')

    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    start_time = time.time()

    output_schema = parse_schema(SEQUENCE_RECORD)

    # read the FASTQ files
    with open_compressed(args.cell_ranger_vdj_path + '/filtered_contig_annotations.csv', 'rt') as filtered_contig, \
         open_compressed(args.cell_ranger_vdj_path + '/filtered_contig.fastq', 'rt') as filtered_sequences:
        
        cell_umi_count = {} # max UMI count for this cell
        cell_contig    = {} # contig name with the max UMI count

        for row in csv.DictReader(filtered_contig):
            # some basic filteres
            if row['is_cell'] == 'True' and row['high_confidence'] == 'True' and \
               row['chain'] == 'IGH' and row['productive'] == 'True':
                # extract columns
                cell = row['barcode']
                umis = int(row['umis'])
                # for each cell, record the contig with the most UMIs
                if cell in cell_umi_count:
                    if umis >= cell_umi_count[cell]:
                        cell_umi_count[cell] = umis
                        cell_contig[cell] = row['contig_id']
                else:
                    cell_umi_count[cell] = umis
                    cell_contig[cell] = row['contig_id']

        # load the sequences for each contig
        sequences = {}
        for contig_id, contig_seq, contig_qual in FastqGeneralIterator(filtered_sequences):
            sequences[contig_id] = (contig_seq, contig_qual)


        seq_records = make_seq_records(cell_umi_count, cell_contig, sequences, subject=args.subject, sample=args.sample, source=args.source)

        output_schema = parse_schema(SEQUENCE_RECORD)
        writer(sys.stdout.buffer, output_schema, seq_records, codec='bzip2')

    elapsed_time = time.time() - start_time
    logging.info('elapsed time %s', time.strftime('%H hours, %M minutes, %S seconds', time.gmtime(elapsed_time)))
    
if __name__ == '__main__':
    sys.exit(main())
