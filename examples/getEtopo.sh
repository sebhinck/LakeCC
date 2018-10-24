#!/bin/bash 

DataFolder="."

mkdir -p $DataFolder

fname="ETOPO1_Bed_c_gmt4"
ncfile="${DataFolder}/${fname}.nc"

if [ ! -f ${ncfile} ]; then

  grdfile="${DataFolder}/${fname}.grd"
  if [ ! -f ${grdfile} ]; then
    wget -nc https://www.ngdc.noaa.gov/mgg/global/relief/ETOPO1/data/bedrock/cell_registered/netcdf/ETOPO1_Bed_c_gmt4.grd.gz -P $DataFolder
    gunzip $DataFolder/ETOPO1_Bed_c_gmt4.grd.gz
  fi
  
  cdo -f nc copy ${grdfile} ${ncfile}
fi

