#!/usr/bin/env python3.6
import sys,time,re,os
import numpy  as np
import pandas as pd
import pysam
import pathlib
from optparse import OptionParser
import support_functions as pf
from multiprocessing import Pool


def extract_cellumi(fh_tup):
  bam_fh,results_dir = fh_tup
  sample = bam_fh.split('/')[-3]
  sample_cellumi_fh = results_dir + sample + '.csv'
  
  print("CREATING:\t",sample_cellumi_fh)
  
  OUT = open(sample_cellumi_fh,'w')
  OUT.write("read,cell_barcode,umi_seq\n")
  
  samfile = pysam.AlignmentFile(bam_fh, "rb")
  for read in samfile.fetch():
    read_id = read.qname
    tag_array = read.tags
    cell_barcode = ""
    umi          = ""
  
    for k,v in tag_array:
      if k == "CB":
        cell_barcode = v
      elif k == "UB":
        umi = v
      else:
        continue
    entry = "%s,%s,%s\n" % (read_id,cell_barcode,umi)
    OUT.write(entry)
  
  OUT.close()
  
  

if __name__ == '__main__':
  usage = "\n<PATH>/%prog -h"
  parser = OptionParser(usage=usage)
  parser.add_option("-i", "--input", default = False, dest="i", help="Input Cellranger VDJ Results Directory, Default = False")
  parser.add_option("-o", "--output", default = "./results", dest="o", help="Output Directory, Default = ./results")
  parser.add_option("-t", "--threads", default = 1, dest="t", help="Thread count, Default = 1")
  (opt, args) = parser.parse_args()

  input_vdj_dir    = opt.i         # Cellranger VDJ output
  results_dir      = opt.o         # Results directory hub
  THREADS          = int(opt.t)    # Threads

  if opt.i == False:
	  sys.exit("\nInvalid Arguements! Must use [-i], option [-o] recommended. Use [-h] for help\n")
  
  # Create list of BAM files
  bam_list = []
  sample_hash = pf.AutoVivification()

  # Create nested Results Directory
  if results_dir[-1:] != '/':
    results_dir += '/'
  results_dir += "CellUMI_files/"
  if os.path.isdir(results_dir) == False:
    pathlib.Path(results_dir).mkdir(parents=True, exist_ok=True)
    #os.mkdir(results_dir)
  
  dir_samples = os.listdir(input_vdj_dir)
  for sample in dir_samples:
    bam_file = input_vdj_dir + sample + "/outs/all_contig.bam"
    sample_hash[sample] = bam_file
    bam_tup = (bam_file,results_dir)
    bam_list.append(bam_tup)
  
  ## Extract cell barcode UMI info from BAM files
  with Pool(THREADS) as p:
    p.map(extract_cellumi,bam_list)

