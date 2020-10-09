#!/usr/bin/env python

from __future__ import print_function

import sys
import argparse
import os.path
import subprocess
import tempfile
from multiprocessing import Pool
import logging
import time

from Bio import SeqIO

from roskinlib import seqclust
from roskinlib.warehouse import DirectoryWarehouse


def concatinate_files(filenames, output_handle):
    for filename in filenames:
        with open(filename, 'rt') as input_handle:
            for line in input_handle:
                output_handle.write(line)

class ClusterProcessor:
    def __init__(self, min_subjects, positive_subjects, negative_subjects):
        self.min_subjects = min_subjects
        self.positive_subjects = positive_subjects
        self.negative_subjects = negative_subjects
    def __call__(self, args):
        v_segment, j_segment, cdr3_length, files = args

        all_subjects = set(self.positive_subjects) | set(self.negative_subjects)

        results = []

        # create a temp dir to hold the clustering files
        with tempfile.TemporaryDirectory() as temp_dir_name:
            # make the input sequences file
            sequence_filename = os.path.join(temp_dir_name, 'sequences.fasta')
            logging.info('writing sequences to %s', sequence_filename)
            with open(sequence_filename, 'wt') as sequence_handle:
                concatinate_files(files, sequence_handle)

            # output filenames
            cluster_reps_filename = os.path.join(temp_dir_name, 'clusters')
            cluster_structure_filename = os.path.join(temp_dir_name, 'clusters.clstr')

            # run CD-HIT
            cdhit = subprocess.Popen(['cd-hit', 
                '-c', '0.90',
                '-n', '5',
                '-d', '0',
                '-l', '4',
                '-S', '0',
                '-G', '1',
                '-g', '1',
                '-b', '1',
                '-t', '0',
                '-i', sequence_filename,
                '-o', cluster_reps_filename],
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            cdhit.communicate()
            assert cdhit.returncode == 0

            # iterate over each cluster
            with open(cluster_structure_filename, 'rt') as clust_struct_handle:
                for cluster in seqclust.CDHITClustIterator(clust_struct_handle):
                    cluster_subjects = set()
                    cluster_lineages = set()
                    cluster_reads = set()
                    cluster_number = int(cluster.name.split(' ')[1])
                    # ... and each member
                    for member in cluster:
                        cluster_reads.add(member.name)  # add the sequence name so we can look it up later
                        # split the read members to get the parts
                        for read_label in member.name.split(','):
                            subject_id, lineage_id, read_id = read_label.split(';')
                            cluster_subjects.add(subject_id)
                            cluster_lineages.add(lineage_id)

                    # make sure extra subject didn't get into the dataset
                    #if not cluster_subjects.issubset(all_subjects):
                    #    for p in cluster_subjects - all_subjects:
                    #        print(p, file=sys.stderr)
                    #    assert cluster_subjects.issubset(all_subjects)

                    if len(cluster_lineages) >= self.min_subjects:
                        sequence_dict = SeqIO.to_dict(SeqIO.parse(sequence_filename, 'fasta'))

                        reads = [(read, str(sequence_dict[read].seq)) for read in cluster_reads]
                        probe_definition = v_segment, j_segment, cdr3_length, cluster_number, reads
                        results.append(probe_definition)

        return results

def filter_groups(root_dir, min_part_count, min_cdr3_len, subjects):
    warehouse = DirectoryWarehouse(root_dir, 'v_segment', 'j_segment', 'cdr3_len', 'subject')

    for signature in warehouse.partitions('.fasta', subject=None):
        v_segment, j_segment, cdr3_len = signature
        cdr3_len = int(cdr3_len)
        if cdr3_len >= min_cdr3_len:
            levels = list(warehouse.partitions('.fasta', *signature))
            # subset by the subjects
            levels = [l for l in levels if l[-1] in subjects]
            if len(levels) >= min_part_count:
                filenames = [warehouse.filename('.fasta', *i) for i in levels]
                yield v_segment, j_segment, cdr3_len, filenames

def main(arguments):
    # program options
    parser = argparse.ArgumentParser(description='',
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    # in/output data
    parser.add_argument('input_warehouse_root_dir', metavar='input-dir', help='the warehouse with the input signatures')
    parser.add_argument('output_warehouse_root_dir', metavar='output-dir', help='the warehouse with the input signatures')
    # probe parameters
    parser.add_argument('--min-subjects', metavar='N', type=int, default=7, help='the minimum number of subjects in a probe')
    parser.add_argument('--min-len',      metavar='L', type=int, default=5, help='the minimum number of amino acids in a probe')
    parser.add_argument('--positive', nargs='+', metavar='P', default=[], help='list of + participants')
    parser.add_argument('--negative', nargs='+', metavar='N', default=[], help='list of - participants')

    args = parser.parse_args(arguments)
    logging.basicConfig(level=logging.INFO)

    if os.path.exists(args.output_warehouse_root_dir):
        logging.fatal('output directory (%s) already exists', args.output_warehouse_root_dir)
        return 10

    subjects = set(args.positive) | set(args.negative)

    filtered_groups = filter_groups(args.input_warehouse_root_dir, args.min_subjects, args.min_len, subjects)

    output_warehouse = DirectoryWarehouse(args.output_warehouse_root_dir,
            'v_segment', 'j_segment', 'cdr3_len', 'cluster')

    processor = ClusterProcessor(args.min_subjects, args.positive, args.negative)
    task_pool = Pool(processes=16)

    results = task_pool.map(processor, filtered_groups)
    for r in results:
        for probe_definition in r:
            v_segment, j_segment, cdr3_length, cluster_number, reads = probe_definition
    
            with output_warehouse.open('.fasta', 'wt', v_segment=v_segment,
                    j_segment=j_segment, cdr3_len=cdr3_length,
                    cluster=cluster_number) as probe_handle:
                for ident, sequence in reads:
                    probe_handle.write('>%s\n%s\n' % (ident, sequence))

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
