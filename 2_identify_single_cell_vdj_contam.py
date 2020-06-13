#!/usr/bin/env python3.6
import sys,time,re,os
import numpy  as np
import pandas as pd
import support_functions as pf
from optparse import OptionParser

if __name__ == '__main__':
  usage = "\n<PATH>/%prog -h"
  parser = OptionParser(usage=usage)
  parser.add_option("-i", "--input", default = False, dest="i", help="VDJ Decontamination Results Directory, Default = False")
  (opt, args) = parser.parse_args()

  results_dir    = opt.i

  if opt.i == False:
	  sys.exit("\nInvalid Arguements! Must use [-i]. Use [-h] for help\n")
  
  # Set Results Directory Path
  if results_dir[-1:] != '/':
    results_dir += '/'
  vdj_cellumi_dir         = results_dir + "CellUMI_files/"
  if os.path.isdir(vdj_cellumi_dir) == False:
    sys.exit("\nCellUMI_files sub-directory does not exist\n")
  results_contam_cells_fh = results_dir + "FLAGGED_contam_cellumi.VDJ.txt"
  
  cell_hash = pf.AutoVivification()
  
  for root,dirs,filenames in os.walk(vdj_cellumi_dir):
	  for file in filenames:
	    sample = file.split('.')[0]
	    fh     = os.path.join(root,file)
	    print(">> PROCESSING:\t",sample, "\t", fh)
	    start = time.time()
	    
	    sample_df = pd.read_csv(fh)
	    sample_df['cellumi'] = sample_df['cell_barcode'].map(str) + '_' + sample_df['umi_seq'].map(str)
	    cellumi_array = np.array(sample_df['cellumi'])
	    cellumi_array = np.unique(cellumi_array,return_counts=True)
	    for i in range(len(cellumi_array[0])):
	      cellumi = cellumi_array[0][i]
	      count   = cellumi_array[1][i]
	      cell_hash[cellumi][sample] += count
	    end = time.time()
	    print("Time (min) =  ", (end - start)/60)
      
  print("\n>> Aggregate all contamination and write to output file")
  OUT = open(results_contam_cells_fh,'w')
  for cellumi in cell_hash:
    count = 0
    sample_str = ""
    for sample in cell_hash[cellumi]:
      count += 1
      read_count = cell_hash[cellumi][sample]
      sample_str += sample +  '=' + str(read_count) + ':'
    sample_str = sample_str[:-1]
    entry = "%s\t%s\n" % (cellumi,sample_str)
    if count > 1:
      OUT.write(entry)
    
  OUT.close()
    
      
	    
	    


