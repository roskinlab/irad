#!/usr/bin/bash

DIR=${1:-.}

cut -d , -f 2 ${DIR}/barcodes | tail -n +2 | sort | uniq
