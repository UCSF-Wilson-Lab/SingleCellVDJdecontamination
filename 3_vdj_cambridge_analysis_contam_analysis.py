#!/usr/bin/env python3.6
import sys,time,re,os
import numpy  as np
import pandas as pd
import support_functions as pf
from optparse import OptionParser

# PURPOSE: implement the Cambrige Method for Identifying which sample has sufficient cell-UMI contamination

# Function that takes a formatted string (sample=[read count]:sample=[read count] ) and returns sample with the highest percentage of reads
def get_sample_with_highest_swap_fraction(contam_str, CONTAM_THRESH):
  sample_list  = contam_str.split(':')
  sample_array = np.array([x.split('=')[0] for x in sample_list])
  info_array   = np.array([x.split('=') for x in sample_list])
  
  sample_to_keep = ""
  max_count  = 0
  sum_counts = 0
  for s,c in info_array:
    c = int(c)
    sum_counts += c
    if c > max_count:
      max_count = c
      sample_to_keep = s
    
  swap_frac      = float(max_count/sum_counts)
  # if one sample is equal or greater than the set threshold, keep that sample, but remove the cell-UMI from the remaining samples
  # if no sample passes the threshold for a given cell-UMI, remove this cell-UMI from all samples contaminated with it
  if swap_frac >= CONTAM_THRESH:
        sample_array_bool = [x != sample_to_keep for x in sample_array]
        sample_array = sample_array[sample_array_bool]
  
  return(sample_array)
  

# Collects all Read IDs assiated with a set of cell-UMIs for a given patient
def get_all_read_IDs_using_cellUMIs(cellumi_array,fh):
  sample_df = pd.read_csv(fh)
  sample_df['cellumi'] = sample_df['cell_barcode'].map(str) + '_' + sample_df['umi_seq'].map(str)
  new_sample_df = sample_df.set_index(keys='cellumi')
  # Intersect all cell-UMIs in the sample with array of contaminated cell-UMIs
  inBothIndex = set.intersection(set(new_sample_df.index), set(cellumi_array))
  target_array = np.array(list(inBothIndex))
  
  # Subset sample Data frame by cell-UMIs in target_array
  sample_df_sub = new_sample_df[new_sample_df.index.isin(target_array)]
  reads_to_rm_array = np.unique(np.array(sample_df_sub["read"]))
  
  return(reads_to_rm_array)


if __name__ == '__main__':
  usage = "\n<PATH>/%prog -h"
  parser = OptionParser(usage=usage)
  parser.add_option("-i", "--input", default = False, dest="i", help="VDJ Decontamination Results Directory, Default = False")
  parser.add_option("-t", "--thresh", default = 0.8, dest="t", help="Rotia Contamination Threshold, Default = 0.8")
  (opt, args) = parser.parse_args()

  results_dir   = opt.i
  CONTAM_THRESH = float(opt.t)    # Threshold of percentage depth to keep a sample for a given contaminated cell-UMI

  if opt.i == False:
	  sys.exit("\nInvalid Arguements! Must use [-i], option [-o] recommended. Use [-h] for help\n")
  
  # INPUT
  if results_dir[-1:] != '/':
    results_dir += '/'
  vdj_contam_results    = results_dir + "FLAGGED_contam_cellumi.VDJ.txt"
  read_info_cellumi_dir = results_dir + "CellUMI_files/"
  
  # OUTPUT DIRECTORY
  reads_to_rm_output_dir = results_dir + "reads_to_remove/"
  if os.path.isdir(reads_to_rm_output_dir) == False:
    os.mkdir(reads_to_rm_output_dir)

  # 1. for each cell-UMI figure out which samples it needs to be removed from using the Cambridge method
  print(">>> Cambridge analysis:\n")
  start = time.time()
  results_dict = pf.AutoVivification()
  
  with open(vdj_contam_results, 'r') as IN:
    for line in IN:
      line = line[:-1]
      cellumi,contam_str = line.split("\t")
      sample_rm_array = get_sample_with_highest_swap_fraction(contam_str, CONTAM_THRESH)
      
      for sample in sample_rm_array:
        results_dict[sample][cellumi] +=1
        
  IN.close()
  end = time.time()
  print("Time (min) =  ", (end - start)/60)
  
  
  # 2. extract read IDs for all cell-UMIs that need to be removed
  print(">>> Extract read IDs that make up each contaminated cell-UMI:\n")
  
  for sample in results_dict:
    print("PROCESSING:\t",sample,"\n")
    start = time.time()
    
    read_to_rm_fh = reads_to_rm_output_dir + sample + ".txt"
    OUT = open(read_to_rm_fh,'w')
    
    start = time.time()
    cellumi_array = np.array(list(results_dict[sample].keys()))
    fh_read_info = read_info_cellumi_dir + sample + '.csv'
    
    read_id_array = get_all_read_IDs_using_cellUMIs(cellumi_array,fh_read_info)
    for read in read_id_array:
      entry = "%s\n" % (read)
      OUT.write(entry)
    
    OUT.close()
    end = time.time()
    print("Time (min) =  ", (end - start)/60)
    
    
  
  
  
  



