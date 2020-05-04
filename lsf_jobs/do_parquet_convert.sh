#!/usr/bin/bash

SORTER=/data/RoskinLab/irbase/pipeline/sort_seq_records.py

SOURCE=${1?the source Avro file must be given}
TARGET=${2?the destination Avro file must be provided}

LABEL=$(basename "${SOURCE}" .avro)

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 2:00
#BSUB -M 16000
#BSUB -J sort_${LABEL}

${SORTER} ${SOURCE} >${TARGET}
EOF
