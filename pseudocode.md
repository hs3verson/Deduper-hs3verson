# Deduper Pseudocode

## Problem

PCR amplification during library prep creates multiple copies of the same original segment of DNA/RNA. If more than one copy gets sequenced, that segments abundance will appear incorrectly high, impacting expression analysis down the line. 

Goal: given a SAM file of uniquely mapped single-end reads, write a new SAM file that keeps only one copy of each PCR duplicate. Reads with UMIs not in the known list of 96 UMIs are thrown out. 

Two reads are PCR duplicates if they have the same:
- chromosome (RNAME, col 3)
- strand (FLAG, col 2, bit 16)
- 5' start position, adjusted for soft clipping, and dependent on if strand is fwd or rev (POS col 4 + CIGAR col 6 + FLAG col 2, bit 16)
- UMI (end of QNAME, col 1)

Adjusting the 5' start:
- Forward strand: start = POS - left soft clip
  - POS 111, CIGAR 14M -> 111 - 0 = 111
  - POS 113, CIGAR 2S12M -> 113 - 2 = 111
  - POS 200, CIGAR 10M5S -> 200 - 0 = 200 (right soft clip ignored (3' end))

- Reverse strand: start = POS + (M, D, N lengths) + right soft clip - 1
  (insertions and left soft clips are ignored (3' end))
  - POS 100, CIGAR 10M -> 100 + 10 - 1 = 109
  - POS 100, CIGAR 8M2S -> 100 + 8 + 2 - 1 = 109
  - POS 100, CIGAR 3S10M -> 100 + 10 - 1 = 109 (left soft clip ignored)
  - POS 100, CIGAR 5M2I5M -> 100 + 5 + 5 - 1 = 109 (insertion ignored)
  - POS 100, CIGAR 5M2D5M -> 100 + 5 + 2 + 5 - 1 = 111 (deletion counted)
  - POS 100, CIGAR 5M100N5M -> 100 + 5 + 100 + 5 - 1 = 209 (N counted)

## Strategy

Sort the input file first with samtools sort so all reads from a chromosome are grouped together. Read the file one line at a time and keep a set of tuples (UMI, strand, adjusted start) for the current chromosome. If a read's tuple has already been seen, it's a duplicate and is skipped. Otherwise write out the read to the output file and add the tuple to the set. Clear the set when the chromosome changes for memory.

## Pseudocode

```
samtools sort input file

store known UMIs in a set

with open input file to read from and output file to write to
current_chrom = None
seen = empty set

for each line in input file:

    if line starts with "@" (header lines):
        write line to output
    else:
        split line by tabs
        qname = column 1
        flag  = column 2
        chrom = column 3
        pos   = column 4
        cigar = column 6

        umi = get_umi(qname) --- see function below

        if umi not in known_umis set:
            continue (skip the read)
        else:
            if chrom is not current_chrom:
                seen = empty set (empty the set for the new chromosome)
                current_chrom = chrom (set current_chrom to be the new one)

            strand = get_strand(flag) --- see function below
            start = get_five_prime_start(pos, cigar, strand) --- see function below
            read_id = (umi, strand, start), tuple

            if read_id in seen:
                skip read (duplicate)
            else:
                add read_id to seen
                write line to output
```

## Functions
```
def get_umi(qname):
    '''Returns the UMI from the end of the QNAME given the QNAME (col 1)'''
    return umi
```
Example: "NS500451:154:HWKTMBGXX:1:11101:15364:1139:GAACAGGT" -> "GAACAGGT"

```
def get_strand(flag):
    '''Returns "-" if bit 16 is set in the flag (16), returns "+" if bit 16 is not set in the flag (0)'''
    return strand ("-" or "+")
```
Examples: 0 -> "+", 16 -> "-"

```
def get_five_prime_start(pos, cigar, strand):
    '''Returns the 5' start position of the read, adjusted for soft clipping'''
    return start
```
Examples:
- 113, "2S12M", "+" -> 111
- 111, "14M", "+" -> 111
- 100, "10M", "-" -> 109
- 100, "8M2S", "-" -> 109
- 100, "3S20M500N10M2S", "-" -> 631
- 100, "5M2I5M", "-" -> 109