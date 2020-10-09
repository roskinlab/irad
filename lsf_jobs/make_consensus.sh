#!/bin/bash

PROBE=${1?please provide probe .fasta file}

LABEL=${PROBE%%.fasta}
LABEL=${LABEL/probes\/split??_fold??\//}

cat <<EOF
~/irbase/analysis/simple_probe_consensus.py ${PROBE} "probe;${LABEL};" >${PROBE%%.fasta}.probe 
EOF
