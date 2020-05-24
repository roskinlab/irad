#!/usr/bin/bash

DATABASE=/data/RoskinLab/irep/phix/genome.fasta
PARSER=/data/RoskinLab/irbase/pipeline/sam_align_score.py

BATCH_NUMBER=${1?the six digit batch number must be given}
if [ ${#BATCH_NUMBER} -ne 6 ] ; then
    echo "batch number must be 6 digits"
    exit
fi

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J phix_${BATCH_NUMBER}

module load bwa

bwa mem -M -p ${DATABASE} batch${BATCH_NUMBER}.fq1.gz | ${PARSER} | gzip >batch${BATCH_NUMBER}.phix1.gz
bwa mem -M -p ${DATABASE} batch${BATCH_NUMBER}.fq2.gz | ${PARSER} | gzip >batch${BATCH_NUMBER}.phix2.gz
EOF
