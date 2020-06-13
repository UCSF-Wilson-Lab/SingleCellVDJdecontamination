#!/usr/bin/perl
use strict;
use warnings 'FATAL' => 'all';
use DataBrowser;

# Purpose: 
#  - remove reads with contaminated cell-UMIs from raw FASTQ file
die "
Usage: $0 <input FASTQ GZ> <list of reads to remove> <Results Dir>

Ex:
  DEV_read_remover.pl 
      <PATH>/sample1_R1.fastq.gz
      <PATH RESULTS>/reads_to_remove/sample1_R1.txt
      <PATH RESULTS>
      <PATH RESULTS>/removed_reads/

" unless @ARGV == 4;
my ($FASTQ,$READS_TO_RM,$RESULTS_DIR,$REMOVED_READS_DIR) = @ARGV;
$RESULTS_DIR       .= '/' if $RESULTS_DIR !~ /\/$/;
$REMOVED_READS_DIR .= '/' if $REMOVED_READS_DIR !~ /\/$/;

my $sample = $FASTQ;
if ($sample =~ /\//){
  $sample  = (split /\//, $sample)[-1];
}
$sample = (split /\./, $sample)[0];

my $output_fh     = $RESULTS_DIR . $sample . ".fastq";
my $reads_removed = $REMOVED_READS_DIR . $sample . ".txt";

# Store Contam read IDs
my %bad_reads;
open(my $CONTAM, "<", $READS_TO_RM) or die;
while (<$CONTAM>){
  chomp;
  $bad_reads{$_}++;
}
close $CONTAM;


# Remove Bad reads from FASTQ
open(my $OUT, ">", $output_fh) or die "Cannot open output file\n";
open(my $OUT2, ">", $reads_removed) or die "Cannot open output file for reads removed\n";

# option 1
#open(my $IN, "<", $FASTQ) or die "Cannot read FASTQ\n";
# opttion 2
open(my $IN, "gunzip -c $FASTQ |") or die "Cannot pipe zipped FASTQ\n";

while (1){
  my $id     = <$IN>;
  last if !defined $id;
  my $seq    = <$IN>;
  my $strand = <$IN>;
  my $qual   = <$IN>;
  
  my $read_id = $id;
  ($read_id)  = $id =~ /(\S+)/;
  $read_id =~ s/@//;
  

  if (!defined $bad_reads{$read_id}){
    print $OUT $id;
    print $OUT $seq;
    print $OUT $strand;
    print $OUT $qual;
  } else{
    # Contaminated reads
    print $OUT2 "$read_id\n";
  }
}

close $IN;
close $OUT;
close $OUT2;

# Zip cleaned FASTQ
system("gzip $output_fh") == 0 or die;

