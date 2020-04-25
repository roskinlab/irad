#!/usr/bin/bash

DIR=${1:-.}

ls ${DIR}/batch??????.fq1.gz | grep -o "[0-9]\{6\}"
