#!/usr/bin/env python3.6
import sys,time,re,os
import numpy  as np
import pandas as pd
import pysam
import pathlib
import subprocess
import gzip
import support_functions as pf
from multiprocessing import Pool
from optparse import OptionParser

# PURPOSE: full 10X VDJ Decontamination Pipeline

if __name__ == '__main__':
  usage = "\n<PATH>/%prog -h"
  parser = OptionParser(usage=usage)
  parser.add_option("-i", "--input", default = False, dest="i", help="Input Cellranger VDJ Results Directory, Default = False")
  parser.add_option("-f", "--fastq", default = False, dest="f", help="Input Raw FASTQ Directory, Default = False")
  parser.add_option("-o", "--output", default = "./results", dest="o", help="Output Directory, Default = ./results")
  parser.add_option("-t", "--thresh", default = 0.8, dest="t", help="Rotia Contamination Threshold, Default = 0.8")
  parser.add_option("-c", "--threads", default = 1, dest="c", help="Thread count, Default = 1")
  (opt, args) = parser.parse_args()

  input_vdj_dir    = opt.i
  sc_vdj_fastq_dir = opt.f
  results_dir      = opt.o        # Results directory hub
  THREADS          = str(opt.c)   # Threads
  CONTAM_THRESH    = str(opt.t) # Threshold of percentage depth to keep a sample for a given contaminated cell-UMI


  if opt.i == False:
	  sys.exit("\nInvalid Arguements! Must use [-i,-f], option [-o] recommended. Use [-h] for help\n")
  
  if results_dir[-1:] != '/':
    results_dir += '/'
  
  
  ### 1. Extract CellUMIs from BAM files
  print("\n>> 1. Extract CellUMI info from Celranger VDJ BAM files\n\n")
  #subprocess.call(["1_vdj_single_cell_BAM_to_cellUMIs.py","-i",input_vdj_dir,"-o",results_dir,"-t",THREADS])
  
  ### 2. Find all contaminated CellUMIs
  print("\n>> 2. Find and list all contaminated CellUMIs\n\n")
  #subprocess.call(["2_identify_single_cell_vdj_contam.py","-i",results_dir])
  
  ### 3. Determine which reads to keep
  print("\n>> 3. Find and list all contaminated CellUMIs\n\n")
  subprocess.call(["3_vdj_cambridge_analysis_contam_analysis.py","-i",results_dir,"-t",CONTAM_THRESH])
  
  ### 4. Remove contaminated reads from raw FASTQs
  print("\n>> 4. Remove contaminated reads from raw FASTQs\n\n")
  subprocess.call(["4_remove_contam_cellUMIs_from_raw_FASTQs.py","-i",input_vdj_dir,"-f",sc_vdj_fastq_dir,"-o",results_dir,"-t",THREADS])

  print("\n>>> DONE! <<<\n")

  
