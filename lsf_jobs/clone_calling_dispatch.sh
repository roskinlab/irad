#!/usr/bin/bash

SEQ_IDENTITY=0.9

/data/RoskinLab/irbase/lsf_jobs/do_clone_clustering.sh ${SEQ_IDENTITY} "$@" | bsub
