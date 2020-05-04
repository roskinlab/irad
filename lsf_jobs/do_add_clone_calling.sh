#!/usr/bin/bash

CLONE_CALLING=/data/RoskinLab/irbase/pipeline/clone_calling.py

SOURCE=${1?the source Avro file must be given}
CLUST_DIR=${2?directoy with the clustering files must be given}
CLONE_LABEL=${3?the clone calling lineage label must be provided}
TARGET=${4?the destination Avro file must be provided}

LABEL=$(basename "${SOURCE}" .avro)

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 8:00
#BSUB -J clone_${LABEL}

find ${CLUST_DIR} -name "seq_*_*_*.clust" | \
${CLONE_CALLING} ${SOURCE} ${CLONE_LABEL} >${TARGET}
EOF
