#!/bin/sh
#SBATCH --job-name="ALAAM_obs"
#SBATCH --time=0-00:00:05
#SBATCH --output=alaam_obs_highschool-%j.out
#SBATCH --error=alaam_obs_highschool-%j.err
#SBATCH --ntasks=1
#SBATCH --mem=500MB

echo -n "started at: "; date
uname -a


# module version numbers are required on OzStar (Ngarrgu Tindebeek)
module load foss/2022b
module load python/3.10.8
module load numpy/1.24.2-scipy-bundle-2023.02

ROOT=${HOME}
export PYTHONPATH=${ROOT}/ALAAMEE/python:${PYTHONPATH}

# output file of simulated ALAAM statistics
OBSTATS_FILE=obs_stats_sim_highschool.txt

time python3 ./computeALAAMstatisticsHighSchool.py | tee ${OBSTATS_FILE}

echo -n "ended at: "; date
