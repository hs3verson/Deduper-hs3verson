#!/bin/bash

#SBATCH --account=bgmp
#SBATCH --partition=bgmp
#SBATCH --cpus-per-task=16
#SBATCH --job-name=deduper
#SBATCH --time=12:00:00
#SBATCH --output=deduper_%j.out

INPUT="/projects/bgmp/hvsev/bioinfo/Bi624/Deduper-hs3verson/C1_SE_uniqAlign.sorted.sam"
OUTPUT="/projects/bgmp/hvsev/bioinfo/Bi624/Deduper-hs3verson/C1_SE_uniqAlign.deduped.sorted.sam"
UMI="/projects/bgmp/hvsev/bioinfo/Bi624/Deduper-hs3verson/STL96.txt"

/usr/bin/time -v python /projects/bgmp/hvsev/bioinfo/Bi624/Deduper-hs3verson/deduper.py -f $INPUT -o $OUTPUT -u $UMI