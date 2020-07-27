#!/usr/bin/bash

BARCODES=${1:-.}

cut -d , -f 2 ${BARCODES} | tail -n +2 | sort | uniq
