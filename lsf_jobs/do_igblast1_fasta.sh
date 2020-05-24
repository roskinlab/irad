#!/bin/bash

FASTA_FILE=${1?the input FASTA file must be given}
SPECIES=${2-human}
CHAIN=${3-ig}
SUBCHAIN=${4-_h}

IGDATA=/data/RoskinLab/programs/igblast_release/
NUM_ALIGN=1
DB_ROOT=/data/RoskinLab/data/imgt
OUTPUT_FILE=${FASTA_FILE%.fasta}
OUTPUT_FILE=${OUTPUT_FILE%.fa}

cat <<EOF
export IGDATA=${IGDATA}

/data/RoskinLab/programs/igblast_release/igblastn \
    -germline_db_V ${DB_ROOT}/${SPECIES}_gl_V -num_alignments_V ${NUM_ALIGN} -germline_db_V_seqidlist ${DB_ROOT}/${SPECIES}_${CHAIN^^}${SUBCHAIN^^}_ids \
    -germline_db_D ${DB_ROOT}/${SPECIES}_gl_D -num_alignments_D ${NUM_ALIGN} -germline_db_D_seqidlist ${DB_ROOT}/${SPECIES}_${CHAIN^^}${SUBCHAIN^^}_ids \
    -germline_db_J ${DB_ROOT}/${SPECIES}_gl_J -num_alignments_J ${NUM_ALIGN} -germline_db_J_seqidlist ${DB_ROOT}/${SPECIES}_${CHAIN^^}${SUBCHAIN^^}_ids \
    -organism ${SPECIES} -ig_seqtype ${CHAIN^} -num_clonotype 0 \
    -auxiliary_data /data/RoskinLab/programs/igblast_release/optional_file/${SPECIES}_gl.aux \
    -query ${FASTA_FILE} | gzip >${OUTPUT_FILE}.igblast.gz
EOF
