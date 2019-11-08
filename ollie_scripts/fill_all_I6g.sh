#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH --array=0-240%36        # Years from 1990 to 2010 
#SBATCH --output=result_%A_%a.out
#SBATCH -p smp

module load python gdal centoslibs

idir="/home/ollie/shinck/projects/Evan/Ice6G"
topodir="/home/ollie/shinck/projects/Evan/rtopo2"
odir="/home/ollie/shinck/projects/Evan/Ice6G/lakes"

Filters=(0 5 10 15 20)
Years=(0 500 1000 1500 2000 2500 3000 3500 4000 4500 5000 5500 6000 6500 7000 7500 8000 8500 9000 9500 10000 10500 11000 11500 12000 12500 13000 13500 14000 14500 15000 15500 16000 16500 17000 17500 18000 18500 19000 19500 20000 20500 21000 22000 23000 24000 25000 26000)

COUNTER=$SLURM_ARRAY_TASK_ID

NF=$(echo "scale=0; $COUNTER % 5"|bc -l)
NY=$(echo "scale=0; $COUNTER / 5"|bc -l)

FILTER=${Filters[$NF]}
YEAR=${Years[$NY]}

srun ./FillLakes_publication.py -y $YEAR -f $FILTER -dz 0.2 -i $idir -t $topodir -o $odir
