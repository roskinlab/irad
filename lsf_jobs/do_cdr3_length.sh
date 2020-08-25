#!/usr/bin/bash

CDR3_LENGTH=~/irbase/analysis/cdr3_length.py

PARSE_LABEL=${1?please provide the parser label to use}
LINEAGE_LABEL=${2?please provide the lineage label to use}

cat <<EOS
#BSUB -L /bin/bash
#BSUB -W 2:00

${CDR3_LENGTH} ${PARSE_LABEL} --lineage ${LINEAGE_LABEL} source=*.clones.igblast.avro >cdr3_length.tsv
EOS
