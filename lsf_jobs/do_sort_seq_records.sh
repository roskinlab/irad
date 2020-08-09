#!/usr/bin/bash

SORTER=~/irbase/pipeline/sort_seq_records.py
DATA_DIR=${1?directory to store dataset has not been set}
shift

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 16:00
#BSUB -M 30000
#BSUB -J sort_${DATA_DIR}
#BSUB -o logs/sort_${DATA_DIR}_%J.log

~/irbase/pipeline/sort_seq_records.py ${DATA_DIR} $@
EOF
