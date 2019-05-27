#!/bin/bash


files=$@


for filename in $files; do
	echo "${filename}..."

	ncap --overwrite -s "t=-t" $filename $filename
	ncatted -a axis,t,o,c,T $filename
	ncatted -a axis,x,o,c,X $filename
	ncatted -a axis,y,o,c,Y $filename
	ncatted -a standard_name,t,o,c,time $filename
	ncatted -a long_name,t,o,c,time $filename
	ncatted -a units,t,o,c,"years since 1950-01-01" $filename
	ncatted -a calendar,t,o,c,"365_day" $filename

done
