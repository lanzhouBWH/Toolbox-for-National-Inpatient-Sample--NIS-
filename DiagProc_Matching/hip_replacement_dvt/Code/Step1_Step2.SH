#!/usr/bin/env bash

#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --mem-per-cpu=32G
#SBATCH -t 12:00:00
#SBATCH --partition bigmem
#SBATCH --array=2016-2020
#SBATCH --output=ooo/study-%j-%a.out
#SBATCH --error=ooo/study-%j-%a.err

echo '-------------------------------'
cd ${SLURM_SUBMIT_DIR}
echo ${SLURM_SUBMIT_DIR}
echo Running on host $(hostname)
echo Time is $(date)
echo SLURM_NODES are $(echo ${SLURM_NODELIST})
echo '-------------------------------'
echo -e '\n\n'

export TOTALPROCS=${SLURM_CPUS_ON_NODE}

module load miniconda3
python3 Step1_Matching.py
python3 Step2_Frequencies.py