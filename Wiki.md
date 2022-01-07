# Overview of *M. truncatula* RNAseq and GWAS analyses and location of source code and data files
The goal of this wiki is to provide a road map for data analysis files, figures, and source code. For a more in-depth description of how to run these analyses please see my [gitlab project here](https://gitlab.com/mclear73/medicago-rnaseq).  
## Description of available RNAseq data files (as of January 7, 2021)
### Input/Reference Files
* [Compiled Raw Count file](https://www.dropbox.com/s/47uxns3am4ywxgv/All_Counts_Raw.csv?dl=0)
* [GMT File for Running GO Term Enrichment](https://www.dropbox.com/s/ikzcd1c5eewqaa5/mtruncatula_v5.gmt?dl=0)
* [Version 5 annotation file (.gff3)](https://www.dropbox.com/s/nywnkx7pdw9iijk/MtrunA17r5.0-ANR-EGN-r1.8.gff3?dl=0)
* [Version 5 assembly file (.fasta)](https://www.dropbox.com/s/3ejs3e3jkpig2f9/mtruna17r5.0-20161119-anr.genome.fasta?dl=0)
* [Compiled Normalized Transcripts per Million (TPM) Count file](https://www.dropbox.com/s/29gp73jzqyn2ylu/All_Counts_TPM.csv?dl=0)
* [Compiled Normalized Fragments per Kilobase Million (FPKM) Count file](https://www.dropbox.com/s/7aemxhmlq58osst/All_Counts_FPKM.csv?dl=0)
* [Metadata associated with samples](https://www.dropbox.com/s/mzc74y7vrl0hcr7/allMetadata.csv?dl=0)
* [Compiled annotation for *M. truncatula*](https://www.dropbox.com/s/405i5dpo63br1mn/M_truncV5_noArab.csv?dl=0). Includes:
	* v4 and v5 gene names
	* Pfam domain, KOG, KEGG, GO, Panther, Interpro annotations
	* Arabidopsis thaliana top blast hit and gene description ***STILL IN PROGRESS***
	* Plant TFDB transcription factor family (if identified as a transcription factor)
* [Name conversion file between v4 and v5 genomes](https://www.dropbox.com/s/kq4dkxjze7sgoxl/MtrunA17r5.0-ANR_geneIDs.txt?dl=0)
### Compiled DEGs with annotation
* [Compiled differentially expressed gene (DEG) file](https://www.dropbox.com/s/m0dgyjnfmj9dm2m/Compiled_DEGs_wAnnotation.csv?dl=0). Includes:
	*  DEGs of treatment versus control samples provided by JGI
	*  DEGs of combined treatments (ex: all Hg-treated root samples)
	*  *M. truncatula* annotation
	*  Assigned Co-expression module for root and leaf co-expression networks (determined by WGCNA)
*  [Overenriched GO-terms in DEG by treatment](https://www.dropbox.com/s/a061h31e1hp07b2/gProfiler_GO_enrichment_REVIGO_FULL.csv?dl=0)
### WGCNA Co-expression Output
*  Leaf co-expression network determined by WGCNA (Probably better to look at the visualization for this information, however the raw node/edge data is deposited here)
	* Leaf WGCNA Node
	* Leaf WGCNA Edge
*  Root co-expression network determined by WGCNA (Probably better to look at the visualization for this information, however the raw node/edge data is deposited here)
	* Root WGCNA Node
	* Root WGCNA Edge
*  Overenriched GO-terms within co-expression modules
	* [Root Revigo output](https://www.dropbox.com/s/q4323sq18jeqm93/Root_WGCNA_gProfiler_GO_enrichment_REVIGO_FULL.csv?dl=0)
	* [Leaf Revigo output](https://www.dropbox.com/s/f9jmnclgjess47d/Leaf_WGCNA_gProfiler_GO_enrichment_REVIGO_FULL.csv?dl=0)  
### Gene Lists
*  Top gene list

### MongoDB Output
*  MongoDB database containing all information  

## Description of available GWAS data files (as of December 21, 2021)
* More to come
* 
* 

## Figures (as of December 7, 2021)
* PCAs of top 1000 most variable genes:
	* Hg-treated root
	* Cd-treated root
	* Hg-treated leaf
	* Cd-treated leaf
* Overenriched GO-terms for DEGs
	* Roots
	* Leaves
* Overenriched GO-terms for WGCNA co-expression networks
	* Roots
	* Leaves   
## Code used to generate data