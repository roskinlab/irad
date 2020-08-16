#!/usr/bin/bash

BATCHER=~/irbase/pipeline/batch_paired_sequences.py

BATCH_DIR=${1?the batch directory must be provided}
READ1_FILE=${2?the sequence file for R1 must be given}
READ2_FILE=${3?the sequence file for R2 must be given}

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 16:00
#BSUB -J batch_${BATCH_DIR}
#BSUB -o logs/batch_${BATCHER}_%J.log

${BATCHER} ${BATCH_DIR} ${READ1_FILE} ${READ2_FILE}
EOF
