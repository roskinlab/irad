#!/usr/bin/bash

INPUT_FASTA=${1:?input FASTA file has not been set}
# the percent identity cutoff
SEQ_IDENTITY=${2:?the min. sequence identity has not been set}

# the type of clustering, 1=single-linkage clustering
CLUST_MODE=1

# create temp. directory to store the clustering files
TMPDIR=$(mktemp -d)

# exit if temp .directory wasn't created successfully
if [ ! -e ${TMPDIR} ]; then
    >&2 echo "Failed to create temp directory"
    exit 1
fi

# ensure temp. directory gets removed even if the script exits abnormally
trap "exit 1"           HUP INT PIPE QUIT TERM
trap 'rm -rf "$TMPDIR"' EXIT

mmseqs easy-cluster --cov-mode 0 -c 1.0 -e inf --min-seq-id ${SEQ_IDENTITY} --cluster-mode ${CLUST_MODE} --alignment-mode 3 --mask 0 ${INPUT_FASTA} ${TMPDIR}/clust ${TMPDIR}/mmseq2
cp ${TMPDIR}/clust_cluster.tsv ${INPUT_FASTA%%.fasta}.clust
