#!/usr/bin/bash

COUNTER=/data/RoskinLab/irbase/pipeline/record_subject_counts.py

INPUT=${1?the sequence record file must be given}
LABEL=$(basename ${INPUT} .avro)

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 4:00
#BSUB -J count_${LABEL}
#BSUB -o logs/count_${LABEL}_%J.log

${COUNTER} ${INPUT} >${INPUT}.counts
EOF
