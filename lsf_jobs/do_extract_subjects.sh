#!/usr/bin/bash

EXTRACTER=/data/RoskinLab/irbase/pipeline/extract_subject_records.py

SOURCE=${1?the source directory must be given}
SUBJECT=${2?the subject must be given}

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 18:00
#BSUB -J extract_${SUBJECT}
#BSUB -o logs/extract_${SUBJECT}_${SOURCE}_%J.log

${EXTRACTER} --append ${SOURCE}/batch??????.records_igblast.avro "subjects/${SUBJECT}.avro" "${SUBJECT}"
EOF
