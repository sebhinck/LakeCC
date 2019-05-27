#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH --array=0-154%36        # Years from 1990 to 2010 
#SBATCH --output=result_%A_%a.out
#SBATCH -p smp

module load python gdal centoslibs

Filters=(0 5 10 15 20)
Years=(0 1000 2000 3000 4000 5000 6000 7000 8000 9000 10000 11000 12000 13000 14000 15000 16000 17000 18000 19000 20000 21000 22000 23000 24000 25000 26000 27000 28000 29000 30000)

COUNTER=$SLURM_ARRAY_TASK_ID

NF=$(echo "scale=0; $COUNTER % 5"|bc -l)
NY=$(echo "scale=0; $COUNTER / 5"|bc -l)

FILTER=${Filters[$NF]}
YEAR=${Years[$NY]}

srun ./FillLakes_Evan.py -y $YEAR -f $FILTER -dz 0.2
