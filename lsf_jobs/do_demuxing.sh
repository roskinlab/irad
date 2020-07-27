#!/usr/bin/bash

DEMUXER=/data/RoskinLab/irbase/pipeline/demuxer.py

SOURCE=${1?the source label must be provided}
BARCODE_MAP=${2?the map provided}

BATCH_NUMBER=${3?the six digit batch number must be given}
if [ ${#BATCH_NUMBER} -ne 6 ] ; then
    echo "batch number must be 6 digits"
    exit
fi

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J ident_${BATCH_NUMBER}

${DEMUXER} ${SOURCE} ${BARCODE_MAP} batch${BATCH_NUMBER}.ident.gz | gzip >batch${BATCH_NUMBER}.demux.gz
EOF
