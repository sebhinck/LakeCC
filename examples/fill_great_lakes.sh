#!/bin/bash

thisdir=$(dirname $0)
libdir=$(readlink -f ${thisdir}/..)

export PYTHONPATH="$libdir:$PYTHONPATH"

EtopoFile="${thisdir}/ETOPO1_Bed_c_gmt4.nc"
GreatLakesFile="${thisdir}/GreatLakes.nc"
OutFile="${thisdir}/GreatLakes_filled.nc"

##get and convert Etopo1 dataset (if not present)
${thisdir}/getEtopo.sh ${thisdir}

##Crop GreatLakes [-93, -73, 40, 49]
${thisdir}/CropAndFilterMap.py ${EtopoFile} ${GreatLakesFile} -93 -73 40 49 'Gaussian' 3

##Use the Python interface to fill the map
#
#Fill lakes
#
#optional arguments:
#  -h, --help            show this help message and exit
#  -i FILE, --input FILE
#                        Input file
#  -o FILE, --output FILE
#                        Output file
#  -sl SL, --sea-level SL
#                        scalar sea-level
#  -dz DZ, --lake_level_spacing DZ
#                        Lake level spacing
#  -zMin ZMIN, --lake_level_min ZMIN
#                        Lowest lake level
#  -zMax ZMAX, --lake_level_max ZMAX
#                        Highest lake level
#  -rho_i RHOI, --ice_density RHOI
#                        Density of ice
#  -rho_s RHOS, --sea_water_density RHOS
#                        Density of sea water
#  -rho_f RHOF, --fresh_water_density RHOF
#                        Density of fresh water
#  -thk_if THK_IF, --icefree_thickness THK_IF
#                        Icefree thickness
#  -tind TIND, --time-index TIND
#                        index of time dimension
#  -ms, --setMarginSink  set margin of domain as sink
#  -nms, --not-setMarginSink
#                        not set margin of domain as sink
#
${libdir}/FillLakes.py -i ${GreatLakesFile} -o ${OutFile} --sea-level 0.0 -dz 10 -zMin -100 -zMax 800

