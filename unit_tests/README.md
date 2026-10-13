# Unit Tests

`input_test.sam` contains 18 reads. `output_test.sam` is what the deduper should produce: 10 reads kept, 7 duplicates removed, 1 read thrown out for UMI with error.

The header and read format come from the example SAM file in the repo. All reads use the same sequence and quality string so that only the fields being tested (QNAME UMI, FLAG, RNAME, POS, CIGAR) change. The file is sorted by chromosome and position to mimic the output of samtools sort.

Since the flowcell coordinates in the QNAME are not used in this code, they were modified to label read numbers for reference: `...:1001:2001:` is read 1 (right before the UMI)

## Header lines

All header lines (`@HD`, `@PG`, `@SQ`) were copied to the output as is.


## Chromosome 2

| Read | POS | CIGAR | Strand | UMI | Start | Result | Why |
|---|---|---|---|---|---|---|---|
| 1 | 100 | 71M | + | AACGCCAT | 100 | kept | first read at this start |
| 2 | 100 | 71M | + | AACGCCAT | 100 | removed | exact duplicate of 1 |
| 3 | 100 | 71M | + | ACGTCATG | 100 | kept | different UMI than 1 |
| 4 | 100 | 71M | - | AACGCCAT | 170 | kept | different strand than 1, therefore different start |
| 5 | 100 | 71M | + | TATAGNGC | 100 | thrown out | UMI not in known list, error |
| 6 | 102 | 2S69M | + | AACGCCAT | 100 | removed | left soft clip makes it match 1 |
| 7 | 105 | 71M | + | AACGCCAT | 105 | kept | different start than 1 |
| 8 | 105 | 66M5S | + | AACGCCAT | 105 | removed | right soft clip ignored on forward, matches 7 |
| 9 | 200 | 71M | - | GAACAGGT | 270 | kept | first read at this start |
| 10 | 200 | 66M5S | - | GAACAGGT | 270 | removed | right soft clip counted, matches 9 |
| 11 | 205 | 5S66M | - | GAACAGGT | 270 | removed | left soft clip ignored on reverse, matches 9 |
| 12 | 250 | 21M50N50M | - | CTGTTCAC | 370 | kept | first read at this start (N's counted) |
| 13 | 300 | 71M | - | CTGTTCAC | 370 | removed | matches 12 |
| 14 | 398 | 35M2D36M | - | TTCGCCTA | 470 | kept | first read at this start (D's counted) |
| 15 | 400 | 71M | - | TTCGCCTA | 470 | removed | matches 14 |
| 16 | 400 | 35M2I34M | - | TTCGCCTA | 468 | kept | I ignored, so start differs from 15 |

## Chromosome 3

| Read | POS | CIGAR | Strand | UMI | Start | Result | Why |
|---|---|---|---|---|---|---|---|
| 17 | 100 | 71M | + | AACGCCAT | 100 | kept | same as 1 but different chromosome |
| 18 | 100 | 3S68M | + | AACGCCAT | 97 | kept | same POS as 17, but soft clip shifts start |

