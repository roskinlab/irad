#!/bin/bash

PARSER=~/irbase/pipeline/parse_igblast.py

BATCH_NUMBER=${1?the six digit batch number must be given}
if [ ${#BATCH_NUMBER} -ne 6 ] ; then
    echo "batch number must be 6 digits"
    exit
fi
PARSE_LABEL=${2?the prase label is required}
SPECIES=${3-human}

DB_ROOT=/data/RoskinLab/data/imgt

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J add_igblast_${BATCH_NUMBER}

${PARSER} ${PARSE_LABEL} ${DB_ROOT}/${SPECIES}_gl_{V,D,J} batch${BATCH_NUMBER}.records.avro \
    batch${BATCH_NUMBER}.igblast.gz >batch${BATCH_NUMBER}.records_igblast.avro
EOF
