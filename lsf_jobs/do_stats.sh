#!/bin/bash

STATS=/data/RoskinLab/irbase/pipeline/sequence_record_stats.py

PARSE_LABEL=${1?the prase label is required}

cat <<EOF
#BSUB -L /bin/bash
#BSUB -W 8:00
#BSUB -J stats

${STATS} -p ${PARSE_LABEL} batch??????.records_igblast.avro >stats
EOF
