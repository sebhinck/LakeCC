#!/bin/bash

thisdir=$(dirname $0)
libdir=$(readlink -f ${thisdir}/..)

export PYTHONPATH="$libdir:$PYTHONPATH"

EtopoFile="${thisdir}/ETOPO1_Bed_c_gmt4.nc"
GreatLakesFile="${thisdir}/GreatLakes.nc"

#get and convert Etopo1 dataset (if not present)
${thisdir}/getEtopo.sh ${thisdir}

#Crop GreatLakes [-93, -73, 40, 49]
${thisdir}/CropAndFilterMap.py ${EtopoFile} ${GreatLakesFile} -93 -73 40 49


