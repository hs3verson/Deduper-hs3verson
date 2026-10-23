#!/bin/bash

#SBATCH --account=bgmp
#SBATCH --partition=bgmp
#SBATCH --cpus-per-task=16
#SBATCH --job-name=deduper
#SBATCH --time=12:00:00
#SBATCH --output=sort_%j.out

/usr/bin/time -v pixi run samtools sort -@ 16 /projects/bgmp/hvsev/bioinfo/Bi624/Deduper-hs3verson/C1_SE_uniqAlign.sam -o /projects/bgmp/hvsev/bioinfo/Bi624/Deduper-hs3verson/C1_SE_uniqAlign.sorted.sam