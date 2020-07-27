#!/usr/bin/bash

MERGER=/data/RoskinLab/irbase/lsf_jobs/merge_paired_reads.sh

BATCH_NUMBER=${1?the six digit batch number must be given}
if [ ${#BATCH_NUMBER} -ne 6 ] ; then
    echo "batch number must be 6 digits"
    exit
fi

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J merge_${BATCH_NUMBER}

${MERGER} ${BATCH_NUMBER}
EOF
