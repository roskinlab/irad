#!/bin/bash

STATS=/data/RoskinLab/irbase/pipeline/sequence_record_stats.py

BATCH_DIR=${1?batch directory is required}
for b in $(~/irbase/lsf_jobs/batches.sh ${BATCH_DIR}) ; do
    prefix=${BATCH_DIR}/batch${b}
    if [ ! -f "${prefix}.fq1.gz" ]; then
        echo "${prefix}.fq1.gz does not exist."
    fi
    if [ ! -f "${prefix}.fq2.gz" ]; then
        echo "${prefix}.fq2.gz does not exist."
    fi
    if [ ! -f "${prefix}.phix1.gz" ]; then
        echo "${prefix}.phix1.gz does not exist."
    fi
    if [ ! -f "${prefix}.phix2.gz" ]; then
        echo "${prefix}.phix2.gz does not exist."
    fi
    if [ ! -f "${prefix}.ident.gz" ]; then
        echo "${prefix}.ident.gz does not exist."
    fi
    if [ ! -f "${prefix}.merged_fq.gz" ]; then
        echo "${prefix}.merged_fq.gz does not exist."
    fi
    if [ ! -f "${prefix}.unmerged_fq.gz" ]; then
        echo "${prefix}.unmerged_fq.gz does not exist."
    fi
    if [ ! -f "${prefix}.demux.gz" ]; then
        echo "${prefix}.demux.gz does not exist."
    fi
    if [ ! -f "${prefix}.records.avro" ]; then
        echo "${prefix}.records.avro does not exist."
    fi
    if [ ! -f "${prefix}.unrecords.avro" ]; then
        echo "${prefix}.unrecords.avro does not exist."
    fi
done
