# Overview of *M. truncatula* RNAseq analyses and location of source code and data files
The goal of this wiki is to provide a road map for data analysis files, figures, and source code. For a more in-depth description of how to run these analyses please see my [gitlab project here](https://gitlab.com/mclear73/medicago-rnaseq).  
## Description of available data files (as of December 7, 2021)
* [Compiled Raw Count file](https://www.dropbox.com/s/zoh1pd23triiiik/Compiled_Raw_Counts.csv?dl=0)
* [Compiled Normalized Transcripts per Million (TPM) Count file](https://www.dropbox.com/s/75zgbeovodft5h4/Compiled_TPM_Counts.csv?dl=0)
* [Metadata associated with samples](https://www.dropbox.com/s/m97i3l0by6076a4/Sample_Metadata.csv?dl=0)
* [Compiled annotation for *M. truncatula*](https://www.dropbox.com/s/73k31q1yekrqcag/Compiled_Annotation.csv?dl=0). Includes:
	* v4 and v5 gene names
	* Pfam domain, KOG, KEGG, GO, Panther, Interpro annotations
	* Arabidopsis thaliana top blast hit and gene description
	* Plant TFDB transcription factor family (if identified as a transcription factor)
* [Compiled differentially expressed gene (DEG) file](https://www.dropbox.com/s/fkibdusk9ya4fcu/All_DE_values_with_annotation.csv?dl=0). Includes:
	*  	DEGs of treatment versus control samples provided by JGI
	*  DEGs of combined treatments (ex: all Hg-treated root samples)
	*  *M. truncatula* annotation
	*  Assigned Co-expression module for root and leaf co-expression networks (determined by WGCNA)
*  Leaf co-expression network determined by WGCNA (Probably better too look at the visualization for this information, however the raw node/edge data is deposited here)
	* [Leaf\_WGCNA\_Node](https://www.dropbox.com/s/ta612v450f8gw21/Root_CytoNode_allMods.txt?dl=0)
	* [Leaf\_WGCNA\_Edge](https://www.dropbox.com/s/dmr2dlz0jig65wq/Leaf_CytoEdge_allMods.txt?dl=0) 
*  Root co-expression network determined by WGCNA (Probably better too look at the visualization for this information, however the raw node/edge data is deposited here)
	* [Root\_WGCNA\_Node](https://www.dropbox.com/s/ta612v450f8gw21/Root_CytoNode_allMods.txt?dl=0)
	* [Root\_WGCNA\_Edge](https://www.dropbox.com/s/y1mqz3i6qhy8snk/Root_CytoEdge_allMods.txt?dl=0)
*  [Overenriched GO-terms in DEG by treatment](https://www.dropbox.com/s/qv64kd4nmuy4ded/DEG_Overenrichment_gProfiler.csv?dl=0)
*  Overenriched GO-terms within co-expression modules
	* [Root Revigo output](https://www.dropbox.com/s/32irt9onkk2ti1t/root_Revigo_output_compiled.csv?dl=0)
	* [Leaf Revigo output](https://www.dropbox.com/s/jnuvtkbjyj9whvn/leaf_Revigo2_output_combined.csv?dl=0)  
*  Top gene list
*  MongoDB database containing all information    

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