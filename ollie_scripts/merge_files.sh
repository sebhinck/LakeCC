#!/bin/bash

module load cdo


directory=$1
filter=$2
outfile=$3


cdo -mergetime ${directory}/*_lakes_filtered${filter}km.nc $outfile
