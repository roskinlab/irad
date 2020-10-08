#!/usr/bin/bash

CONVERTER=~/irbase/pipeline/seq_record_to_parquet.py
SOURCE=${1?the source Avro file must be given}
DATASET_ROOT=${2?the root of the parquet dataset must be given}
LABEL=$(basename "${SOURCE}" .clones.igblast.avro)

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 4:00
#BSUB -M 18000
#BSUB -J parquet_${LABEL}
#BSUB -o logs/parquet_${LABEL}_%J.log

${CONVERTER} ${SOURCE} ${DATASET_ROOT}
EOF
