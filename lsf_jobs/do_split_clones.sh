#!/usr/bin/bash

SPLITER=~/irbase/pipeline/split_for_clone_calling.py

# ~/irbase/pipeline/split_for_clone_calling.py clones igb116hsa source\=roskinlab\:K001.igblast.avro source\=roskinlab\:K002.igblast.avro

BATCH_DIR=${1?the batch directory must be provided}
shift
PARSE_ID=${1?the parse label must be provided}
shift

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 16:00
#BSUB -M 18000
#BSUB -J split_${LABEL}
#BSUB -o split_clone_${BATCH_DIR}_%J.log

${SPLITER} "${BATCH_DIR}" ${PARSE_ID} $@
EOF
