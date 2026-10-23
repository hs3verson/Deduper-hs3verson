#!/bin/bash

#SBATCH --account=bgmp
#SBATCH --partition=bgmp
#SBATCH --cpus-per-task=16
#SBATCH --job-name=deduper
#SBATCH --time=12:00:00
#SBATCH --output=deduper_%j.out

INPUT="/projects/bgmp/shared/deduper/C1_SE_uniqAlign.sam"
OUTPUT="/Users/hansev/bioinfo/Bi624/Deduper-hs3verson"
UMI="/Users/hansev/bioinfo/Bi624/Deduper-hs3verson/STL96.txt"

/usr/bin/time -v python /Users/hansev/bioinfo/Bi624/Deduper-hs3verson/deduper.py -f $INPUT -o $OUTPUT -u $UMI