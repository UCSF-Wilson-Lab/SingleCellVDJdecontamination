#!/usr/bin/env python3.6
import sys,time,re,os
import numpy  as np
import subprocess
import support_functions as pf
import gzip
from multiprocessing import Pool
from optparse import OptionParser

def remove_contam_reads_from_vdj_fastq(fh_tup):
  sample,fh,fastq_dir,results_dir = fh_tup
  master_results_dir  = results_dir + "All_cleaned_vdj_fastqs/"
  sample_results_dir  = os.path.join(master_results_dir,sample) + '/'
  removed_reads_dir   = results_dir + "removed_reads/"
  # Deconamination git repo must be configured to your PATH
  decontam_script     = "fastq_cleaner.pl"
  
  if os.path.isdir(master_results_dir) == False:
    os.mkdir(master_results_dir)
  if os.path.isdir(sample_results_dir) == False:
    os.mkdir(sample_results_dir)
  if os.path.isdir(removed_reads_dir) == False:
    os.mkdir(removed_reads_dir)
  
  print(">>> Processing:\t",sample)
  
  # b. remove contam read IDs from sample FASTQS
  for root,dirs,filenames in os.walk(fastq_dir):
    for file in filenames:
      # Check if file already exists
      output_file_gz = os.path.join(sample_results_dir,file)
      if os.path.isfile(output_file_gz):
        continue
      
      fastq_fh = os.path.join(root,file)

      ## INPUT of perl script: fastq_fh,fh,sample_results_dir
      print("\tDecontaminating =>\t", file)
      subprocess.call([decontam_script,fastq_fh,fh,sample_results_dir,removed_reads_dir])
      

  
  

if __name__ == '__main__':
  usage = "\n<PATH>/%prog -h"
  parser = OptionParser(usage=usage)
  parser.add_option("-i", "--input", default = False, dest="i", help="Input Cellranger VDJ Results Directory, Default = False")
  parser.add_option("-f", "--fastq", default = False, dest="f", help="Input Raw FASTQ Directory, Default = False")
  parser.add_option("-o", "--output", default = "./results", dest="o", help="Output Directory, Default = ./results")
  parser.add_option("-t", "--threads", default = 1, dest="t", help="Thread count, Default = 1")
  (opt, args) = parser.parse_args()

  input_vdj_dir    = opt.i
  sc_vdj_fastq_dir = opt.f
  results_dir      = opt.o      # Results directory hub
  THREADS          = int(opt.t) # Threads

  if opt.i == False:
	  sys.exit("\nInvalid Arguements! Must use [-i,-f], option [-o] recommended. Use [-h] for help\n")
  
  if results_dir[-1:] != '/':
    results_dir += '/'
  
  # INPUT
  contam_reads_dir  = results_dir + "reads_to_remove/"

  # output of samples that are already cleaan
  samples_already_cleaned = results_dir + "samples_already_clean_pre_decontam.txt"

  # 1. Create dictionary of all samples needed for the analysis
  target_samples_hash = pf.AutoVivification()
  target_samples      = os.listdir(input_vdj_dir)

  for sample in target_samples:
    target_samples_hash[sample] += 1
  
  # 2. Create dictionary of sample -> cellranger results directory
  sample_fastq_dir_hash = pf.AutoVivification()
  
  dir_samples = os.listdir(sc_vdj_fastq_dir)

  for sample in dir_samples:
    if sample in target_samples_hash.keys():
      sample_dir = sc_vdj_fastq_dir + sample + "/"
      sample_fastq_dir_hash[sample] = sample_dir
  
  
  # 3. Create list of files with contaminated reads and their corresponding FASTQ directories
  sample_file_list = os.listdir(contam_reads_dir)
  fh_list = [contam_reads_dir + filename for filename in sample_file_list]
  fh_list_tuple = []
  for fh in fh_list:
    filename  = fh.split('/')[-1]
    sample    = filename.split('.')[0]
    fastq_dir = sample_fastq_dir_hash[sample]
    fh_list_tuple.append((sample,fh,fastq_dir,results_dir))
    ### DEBUG: only run one sample
    #break
    ###
  
  
  ### SANITY CHECK ###
  # make sure you have accounted for every sample correctly
  clean_samples = []
  final_sample_list = [s for s,r,f,o in fh_list_tuple]
  for sample in target_samples_hash:
    if sample not in final_sample_list:
      clean_samples.append(sample)
  
  OUT = open(samples_already_cleaned,'w')
  for sample in clean_samples:
    OUT.write("%s\n" % (sample))
    
  OUT.close()
      
  ###

  
  # 4. remove contaminated reads from raw FASTQs
  
  # Single Thread
  #for fh_tup in fh_list_tuple:
  #  remove_contam_reads_from_vdj_fastq(fh_tup)
  
  # Multi-threading
  with Pool(THREADS) as p:
    p.map(remove_contam_reads_from_vdj_fastq,fh_list_tuple)
  
  
  print("\n>>> DONE! <<<\n")
    


