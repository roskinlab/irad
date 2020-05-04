#!/usr/bin/bash

CONVERTER=/data/RoskinLab/irbase/pipeline/seq_record_to_parquet.py
SUBJECT_LIST=/data/RoskinLab/irbase/lsf_jobs/subjects.sh

SOURCE_DIR=${1?direcotry with the Avro files must be given}

LABEL=$(basename "${SOURCE}")

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 8:00
#BSUB -M 16000
#BSUB -J Parquet_convert

EOF
for s in $(${SUBJECT_LIST} ${SOURCE_DIR}) ; do
    echo ${CONVERTER} \"subjects/${s}.avro\"
done
