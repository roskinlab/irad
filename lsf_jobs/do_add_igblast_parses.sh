#!/bin/bash

PARSER=~/irbase/pipeline/parse_igblast.py

PARSE_LABEL=${1?the parse label is required}
SEQ_REC_FILE=${2?please provide a Avro file with the sequence records}
PARSE_DIR=${3?please provide the directory with IgBLAST parses}
DEST_FILE=${4?please provide a filename for the resulting sequence records}


ROOT=/data/RoskinLab/base/parsers/${PARSE_LABEL}/
SPECIES=$(cat ${ROOT}/species)
JOB_LABEL=$(basename "${SEQ_REC_FILE}" .avro)

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 16:00
#BSUB -J add_parse_${JOB_LABEL}
#BSUB -o add_${PARSE_DIR}_%J.log

${PARSER} ${PARSE_LABEL} ${ROOT}/${SPECIES}_gl_{V,D,J} ${SEQ_REC_FILE} ${PARSE_DIR}/batch??????.igblast.${PARSE_LABEL}.gz >${DEST_FILE}
EOF
