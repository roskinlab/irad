#!/usr/bin/bash

BATCHER=~/irbase/pipeline/batch_single_sequences.py

BATCH_DIR=${1?the batch directory must be provided}
SEQ_RECORD=${2?the sequence record Avro filename must be provided}

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J batch_${BATCH_DIR}
#BSUB -o batch_${BATCH_DIR}_%J.log

${BATCHER} --input-format avro "${BATCH_DIR}" "${SEQ_RECORD}"
EOF
