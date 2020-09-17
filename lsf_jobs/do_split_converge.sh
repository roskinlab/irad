#!/usr/bin/bash

SPLITER=~/irbase/pipeline/split_for_convergence_clustering.py

BATCH_DIR=${1?the batch directory must be provided}
shift
PARSE_ID=${1?the parse label must be provided}
shift
LINEAGE_ID=${1?the lineage label must be provided}
shift

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 16:00
#BSUB -M 18000
#BSUB -J splitcon_${BATCH_DIR}
#BSUB -o logs/splitcon_%J.log

${SPLITER} "${BATCH_DIR}" ${PARSE_ID} ${LINEAGE_ID} $@
EOF
