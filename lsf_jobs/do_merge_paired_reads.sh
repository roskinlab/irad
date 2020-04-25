#!/usr/bin/bash

MERGER=/data/RoskinLab/programs/FLASH/flash
MIN_OVERLAP=10
MAX_OVERLAP=100000
MAX_MISMATCH=0.25
THREADS=1

BATCH_NUMBER=${1?the six digit batch number must be given}
echo ${#BATCH_NUMBER}
if [ ${#BATCH_NUMBER} -ne 6 ] ; then
    echo "batch number must be 6 digits"
    exit
fi

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J merge_${BATCH_NUMBER}

${MERGER} --min-overlap=${MIN_OVERLAP} --max-overlap=${MAX_OVERLAP} --max-mismatch-density=${MAX_MISMATCH} \
          --threads=${THREADS} --allow-outies --trim-outies --quiet --compress --to-stdout \
          batch${BATCH_NUMBER}.fq2.gz batch${BATCH_NUMBER}.fq1.gz >batch${BATCH_NUMBER}.merged_fq.gz
EOF
