#!/usr/bin/bash

SPLITER=/data/RoskinLab/irbase/pipeline/split_for_clone_calling.py

BATCH_DIR=${1?the batch directory must be provided}
SEQ_RECORD=${2?the sequence record Avro filename must be provided}
PARSE_ID=${3?the parse label must be provided}

LABEL=$(basename "${SEQ_RECORD}" .avro)

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J split_${LABEL}

${SPLITER} "${BATCH_DIR}" "${SEQ_RECORD}" ${PARSE_ID}
EOF
