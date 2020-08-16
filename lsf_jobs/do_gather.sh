#!/usr/bin/bash

GATHERER=~/irbase/pipeline/gather.py

BATCH_NUMBER=${1?the six digit batch number must be given}
if [ ${#BATCH_NUMBER} -ne 6 ] ; then
    echo "batch number must be 6 digits"
    exit
fi

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J gather_${BATCH_NUMBER}

${GATHERER} batch${BATCH_NUMBER}.merged_fq.gz batch${BATCH_NUMBER}.ident.gz batch${BATCH_NUMBER}.demux.gz \
            batch${BATCH_NUMBER}.phix1.gz batch${BATCH_NUMBER}.phix2.gz >batch${BATCH_NUMBER}.records.avro

${GATHERER} batch${BATCH_NUMBER}.unmerged_fq.gz batch${BATCH_NUMBER}.ident.gz batch${BATCH_NUMBER}.demux.gz \
            batch${BATCH_NUMBER}.phix1.gz batch${BATCH_NUMBER}.phix2.gz --annote-set-true unmerged \
            >batch${BATCH_NUMBER}.unrecords.avro

EOF
