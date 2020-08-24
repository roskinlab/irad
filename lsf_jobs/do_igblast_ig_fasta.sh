#!/bin/bash

PARSE_LABEL=${1?please provide the parser label to use}
INPUT_FILE=${2?please provide the FASTA input file}
NUM_ALIGN=${3:-3}

OUTPUT_FILE=${INPUT_FILE%.fasta}
OUTPUT_FILE=${OUTPUT_FILE%.fa}

cat <<EOF
#BSUB -o parse_${PARSE_LABEL}_%J.log
#BSUB -W 4:00
#BSUB -M 4000

/data/RoskinLab/base/parsers/igblast_ig.sh ${PARSE_LABEL} ${INPUT_FILE} ${NUM_ALIGN} | gzip >${OUTPUT_FILE}.igblast.${PARSE_LABEL}.gz
EOF
