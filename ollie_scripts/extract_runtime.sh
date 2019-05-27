#!/bin/bash

name_prefix=$1
offset=$2
ofile=$3

rm $ofile

for i in $(seq $offset 5 155)
do 
    fname=${name_prefix}_${i}.out
    year=$(echo "scale=0; $i / 5 * 1000"|bc -l)
    sec=$(cat $fname | grep "Lake level caluculation took" | cut -d" "  -f5 | awk -F':' '{print $1 * 60 * 60 + $2 * 60 + $3}')
    echo $year $sec>> $ofile
done
