#!/usr/bin/bash

MERGER=/data/RoskinLab/programs/FLASH/flash
MIN_OVERLAP=10
MAX_OVERLAP=100000
MAX_MISMATCH=0.25
THREADS=1

UNMERGER=/data/RoskinLab/irbase/pipeline/fastq_concat.py

BATCH_NUMBER=${1?the six digit batch number must be given}
if [ ${#BATCH_NUMBER} -ne 6 ] ; then
    echo "batch number must be 6 digits"
    exit
fi

# create temp. directory to store the merged files
TMPDIR=$(mktemp -d)
# exit if temp .directory wasn't created successfully
if [ ! -e ${TMPDIR} ]; then
    >&2 echo "Failed to create temp directory"
    exit 1
fi
# ensure temp. directory gets removed even if the script exits abnormally
trap "exit 1"           HUP INT PIPE QUIT TERM
trap 'rm -rf "$TMPDIR"' EXIT

${MERGER} --min-overlap=${MIN_OVERLAP} --max-overlap=${MAX_OVERLAP} --max-mismatch-density=${MAX_MISMATCH} \
          --threads=${THREADS} --allow-outies --trim-outies --quiet --compress --output-directory=${TMPDIR} \
          batch${BATCH_NUMBER}.fq2.gz batch${BATCH_NUMBER}.fq1.gz
mv ${TMPDIR}/out.extendedFrags.fastq.gz batch${BATCH_NUMBER}.merged_fq.gz
${UNMERGER} ${TMPDIR}/out.notCombined_1.fastq.gz ${TMPDIR}/out.notCombined_2.fastq.gz | gzip >batch${BATCH_NUMBER}.unmerged_fq.gz
