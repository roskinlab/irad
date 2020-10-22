#!/usr/bin/bash

CDR3_LENGTH=~/irbase/analysis/cdr3_length.py

OUTPUT_FILE=${1?please provide the output file}
shift
PARSE_LABEL=${1?please provide the parser label to use}
shift
LINEAGE_LABEL=${1?please provide the lineage label to use}
shift

# make sure the input files exist
for f in "$@" ; do
    if [ ! -f "$f" ]; then
        echo >&2 ${f} does not exists
        exit 1
    fi
done

cat <<EOS
#BSUB -L /bin/bash
#BSUB -W 2:00

${CDR3_LENGTH} ${PARSE_LABEL} --lineage ${LINEAGE_LABEL} >${OUTPUT_FILE} \\
EOS
for f in "$@" ; do
    echo \"${f}\" \\
done
echo
