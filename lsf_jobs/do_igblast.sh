#!/bin/bash

BATCH_NUMBER=${1?the six digit batch number must be given}
echo ${#BATCH_NUMBER}
if [ ${#BATCH_NUMBER} -ne 6 ] ; then
    echo "batch number must be 6 digits"
    exit
fi
SPECIES=${2-human}
CHAIN=${3-ig}
SUBCHAIN=${4-_h}

IGDATA=/data/RoskinLab/programs/igblast_release/
NUM_ALIGN=3
DB_ROOT=/data/RoskinLab/data/imgt

cat <<EOF
export IGDATA=${IGDATA}

/data/RoskinLab/irbase/pipeline/fastq_to_fasta.py -t batch${BATCH_NUMBER}.merged_fq.gz \
| /data/RoskinLab/programs/igblast_release/igblastn \
    -germline_db_V ${DB_ROOT}/${SPECIES}_gl_V -num_alignments_V ${NUM_ALIGN} -germline_db_V_seqidlist ${DB_ROOT}/${SPECIES}_${CHAIN^^}${SUBCHAIN^^}_ids \
    -germline_db_D ${DB_ROOT}/${SPECIES}_gl_D -num_alignments_D ${NUM_ALIGN} -germline_db_D_seqidlist ${DB_ROOT}/${SPECIES}_${CHAIN^^}${SUBCHAIN^^}_ids \
    -germline_db_J ${DB_ROOT}/${SPECIES}_gl_J -num_alignments_J ${NUM_ALIGN} -germline_db_J_seqidlist ${DB_ROOT}/${SPECIES}_${CHAIN^^}${SUBCHAIN^^}_ids \
    -organism ${SPECIES} -ig_seqtype ${CHAIN^} -num_clonotype 0 \
    -auxiliary_data /data/RoskinLab/programs/igblast_release/optional_file/${SPECIES}_gl.aux \
    -query - | gzip >batch${BATCH_NUMBER}.igblast.gz
EOF
