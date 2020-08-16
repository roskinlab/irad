#!/usr/bin/bash

IDENTER=~/irbase/pipeline/identer_read_pairs.py
BARCODES=~/irbase/database/barcodes
TARGETS=~/irbase/database/targets

BATCH_NUMBER=${1?the six digit batch number must be given}
if [ ${#BATCH_NUMBER} -ne 6 ] ; then
    echo "batch number must be 6 digits"
    exit
fi

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J ident_${BATCH_NUMBER}

${IDENTER} --barcodes1 ${BARCODES}/{boydlab_isotype,boydlab_j} \
           --targets1  ${TARGETS}/{biomed2_j,boydlab_ighc} \
           --barcodes2 ${BARCODES}/boydlab_isotype \
           --targets2  ${TARGETS}/{biomed2_fr1,biomed2_fr2} -- \
           batch${BATCH_NUMBER}.fq{1,2}.gz | gzip >batch${BATCH_NUMBER}.ident.gz
EOF
