#!/usr/bin/env python

import argparse
import re

def get_args():
    parser = argparse.ArgumentParser(
        description="Removes PCR duplicates from a SAM file of uniquely mapped, "
                    "single-end reads. Keeps the first read of each set of duplicates.",
        epilog="Assumptions:\n"
            "  - Input SAM file is sorted by chromosome and position (samtools sort)\n"
            "  - Reads are single-end and uniquely mapped\n"
            "  - The UMI is the last colon-separated field of the QNAME\n"
            "  - Reads with UMIs not in the UMI file are discarded\n"
            "  - Duplicates have the same chromosome, strand, UMI, and\n"
            "    soft-clip-adjusted 5' start position",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("-f", "--file", required=True,
                        help="absolute path to the sorted input SAM file")
    parser.add_argument("-o", "--outfile", required=True,
                        help="absolute path for the deduplicated output SAM file")
    parser.add_argument("-u", "--umi", required=True,
                        help="file containing the list of known UMIs, one per line")

    return parser.parse_args()

args = get_args()

# Function to slice the UMI from the QNAME column

def get_umi(qname: str) -> str:
    '''Returns the UMI from the end of the QNAME given the QNAME (col 1)'''
    qname_split = qname.split(":")    # split qname by colons into a list
    umi = qname_split[-1]             # define umi as the last item in the list
    return umi

# Function to extract the strand from the bitwise flag

def get_strand(flag: int) -> str:
    '''Returns "-" if bit 16 is set in the flag, returns "+" if bit 16 is not set in the flag'''
    if (flag) & 16 == 16:    # convert bit 16 from str to int and check if it is "on" -> reverse
        return "-"
    else:
        return "+"

# Function to determine 5' start position

def get_five_prime_start(pos: int, cigar: str, strand: str) -> int:
    '''Returns the 5' start position of the read, adjusted for soft clipping'''
    cigar_components = re.findall(r"(\d+)([A-Z=])", cigar)  # splits CIGAR into a list of (number (length), letter) tuples

    # for forward strand: start = pos minus left soft-clipping (S at start of cigar string)
    if strand == "+":
        if cigar_components[0][1] == "S":               # look at first letter seen in cigar string
            start = pos - int(cigar_components[0][0])   # subtract length attached to S
        else:
            start = pos

    # for reverse strand: start = pos plus M's, D's, and N's plus right soft-clipping (S at end of cigar string) minus one
    else:
        reference_length = 0                             # initialize number of reference genome positions the read spans
        for length, letter in cigar_components:
            if letter in "MDN":                          # if letter in cigar_components tuple is M (match/mismatch), D (deletion), or N (skipped)
                reference_length += int(length)          # add associated length value to reference_length
        right_clip = 0                                   # set right_clip to zero to avoid error when there is no right_clip
        if cigar_components[-1][1] == "S":               # identify right soft-clipping
            right_clip = int(cigar_components[-1][0])    # set right_clip to associated length value
        start = pos + reference_length + right_clip - 1  # calculate final start postiion
    return start


# Create known UMIs set

with open(args.umi, "r") as fh:
    known_umis = set()
    for line in fh:
        known_umis.add(line.strip())

# Command to run while testing:
# ./deduper.py -f unit_tests/input_test.sam -o unit_tests/TESTOUT.sam -u STL96.txt

# Put everything together to dedupe!

with open(args.file, "r") as ifh, open(args.outfile, "w") as ofh:
    # Initialize counters, chromosome variable, and read_ids set
    header_lines = 0
    unique_reads = 0
    wrong_umis = 0
    duplicates_removed = 0
    current_chrom = None
    seen = set()

    for line in ifh:
        # Write out header lines unchanged to output file
        if line.startswith("@"):
            ofh.write(f"{line}")
            header_lines += 1
        # For reads:
        else:
            # Split read (by tabs) into list of the columns
            sam_cols = line.strip().split("\t")
            qname = sam_cols[0]                 
            flag = int(sam_cols[1])
            chrom = sam_cols[2]
            pos = int(sam_cols[3])
            cigar = sam_cols[5]

            # Extract UMI from end of QNAME using fxn
            umi = get_umi(qname)

            # Count then skip UMIs not in known UMIs set
            if umi not in known_umis:
                wrong_umis += 1
                continue
            # For reads with known UMIs:
            else:
                # Reset seen set and current_chrom if chromosome changed
                if chrom != current_chrom:
                    seen = set()
                    current_chrom = chrom
                # Determine strand from bitwise flag using fxn
                strand = get_strand(flag)
                # Determine 5' start position using fxn
                start = get_five_prime_start(pos, cigar, strand)

                # Create tuple with umi, strand, and start to add to set
                read_id = (umi, strand, start)
                # If tuple has been seen -> duplicate -> skip
                if read_id in seen:
                    duplicates_removed += 1
                    continue
                # If tuple has not been seen -> add to set -> write full read to output, add one to unique reads counter
                else:
                    seen.add(read_id)
                    ofh.write(f"{line}")
                    unique_reads += 1
                    
print(f"# of Header Lines = {header_lines}\n# of Unique Reads = {unique_reads}\n# of Wrong UMIs = {wrong_umis}\n# of Duplicates Removed = {duplicates_removed}")




