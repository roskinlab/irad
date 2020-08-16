#!/usr/bin/bash

CLUSTERER=/data/RoskinLab/irbase/lsf_jobs/clone_cluster.sh

SEQ_IDENTITY=${1:?the min. sequence identity has not been set}
shift
INPUT_FASTA=${1:?input FASTA file has not been set}
LABEL=$(basename "${INPUT_FASTA}" .fasta)

cat <<EOF
#BSUB -L /bin/bash
#BSUB -J clone_${LABEL}

module load mmseq2

EOF

for i in "$@"; do
cat <<EOF
${CLUSTERER} ${i} ${SEQ_IDENTITY}
EOF
done
