# -*- coding: utf-8 -*-
"""
Created on Thu Sep  2 16:24:16 2021

@author: mclea
"""

import pandas as pd
import os
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt
import seaborn as sns
from gprofiler import GProfiler
import requests




#This function compiles all of the count files downloaded from JGI
###Instructions: Specifiy a directory and this will compile all of the count.txt
###files within the directory into a single .csv file
###This function will also generate a separate metadata.csv file with all of the 
###sample names so that additional metadata information can be easily provided for
###all count files.
###NOTE: this will compile all *.txt files in the specified directory.
###NOTE: if no directory is provided, it will use the current directory
def compile_Counts(directory=None):
      cwd = os.getcwd() #Get current working directory
      if directory is not None: #Check if a directory input was provided
            input_dir = directory
      else:
            input_dir = cwd
      finalDF = pd.DataFrame() #Create a blank dataframe where we will concatenate the data
      
      for filename in os.listdir(input_dir):
            if filename.endswith('.txt'): #Loop through all *.txt files in the directory
                  file = input_dir + '/' + filename
                  tempDF = pd.read_csv(file,sep='\t', index_col=0)
                  finalDF = pd.concat([finalDF, tempDF], axis=1, join='outer')
      metadataDF = pd.DataFrame() #Create a blank dataframe for metadata file
      sampleList = finalDF.columns.to_list() #Extract a list of column names (i.e., sample names)
      metadataDF['Samples'] = sampleList #Add all sample names to the Samples column
      finalDF.to_csv('All_Counts.csv')
      metadataDF.to_csv('All_Metadata.csv', index=False)

#This function merges annotations files together to produce a single, compiled annotation file
#As of now, it is written to compile the JGI annotation with a transcription factor
#list from plantTFDB.
##NOTE: You are not required to provide any files other than the JGI annotation file      
def compile_Annot(jgiAnnot_file, plantTFDB_file=None, THS_file=None):
      jgiAnnot = pd.read_csv(jgiAnnot_file, sep='\t')
      if plantTFDB_file is not None:
            TF_list = pd.read_csv(plantTFDB_file, delimiter='\t')
            jgiAnnot = jgiAnnot.merge(TF_list, how='left', left_on='locusName', right_on='Gene_ID') #merge TF_list to JGI annotation
            jgiAnnot = jgiAnnot.drop(columns=['Gene_ID']).set_index('locusName')
      if THS_file is not None:
            THS_DF = pd.read_csv(THS_file)
            jgiAnnot = jgiAnnot.merge(THS_DF, how='left', left_index=True,  right_on='Gene') #merge TF_list to JGI annotation
            jgiAnnot = jgiAnnot.drop(columns=['Gene'])
            
      jgiAnnot.to_csv('Compiled_Annotation.csv') #output annotation file
      
      
def get_token_form_response(response):
    if response.status_code == 200:
        token = response.json()['organism']
    else:
        try:
            error_message = 'Error: {}'.format(response.json()['message'])
        except:
            error_message = 'Error, status code {}'.format(response.status_code)
        raise AssertionError(error_message)
    print("Token:", token)
    return token

#This function will extract DEGs that meet a certain Log2 fold-change and p-value
#threshold and then run g:Profiler to find over-represented pathways withing those differentially expressed genes
#you can set the adj. p-value threshold for the over-enrichment analysis or use the defaults
##NOTE: make sure the organism name exactly corresponds to the correct organism name used by
##g:Profiler. These can be found on the organisms list page here: (https://biit.cs.ut.ee/gprofiler_beta/page/organism-list)
def gProfiler_DEGs(DEA_file, org_name, custom_GMT=None, L2FC_threshold=1, adjP_threshold=0.05, gProf_adjP_threshold=0.05):
    if custom_GMT is not None:
          with open(custom_GMT) as f:
              response = requests.post('https://biit.cs.ut.ee/gprofiler/api/gost/custom/',
                                       json={'gmt':f.read(),
                                             'name': custom_GMT})
              token = get_token_form_response(response)
          DEGs = pd.read_csv(DEA_file, index_col=0)
          DEGs = DEGs.apply(lambda col:pd.to_numeric(col, errors='coerce'))
#          DEGs.apply(pd.to_numeric, errors = 'coerce')
          samps = [c for c in DEGs.columns if 'log2FC' in c]
          samps = [s.replace("_log2FC", "") for s in samps]
          LFC_thresh = abs(L2FC_threshold)
          pval_thresh = abs(adjP_threshold)
          finalDF = pd.DataFrame()
          for i in samps:
                cols = [c for c in DEGs.columns if i in c]
                samp_DEG = DEGs[cols]
                lfc_col = [c for c in samp_DEG.columns if 'log2FC' in c][0]
                adjP_col =[c for c in samp_DEG.columns if 'Padj' in c][0]
                samp_DEG = samp_DEG[samp_DEG[adjP_col] <  pval_thresh]
                samp_DEG = samp_DEG[(samp_DEG[lfc_col]> LFC_thresh) | (samp_DEG[lfc_col] < (-LFC_thresh))]
                genes = samp_DEG.index.to_list()
                gp = GProfiler(return_dataframe=True)
                output = gp.profile(organism=token,
                            query= genes,
                            user_threshold=gProf_adjP_threshold)
#                print(output)
                output['Comparison'] = i
                finalDF = pd.concat([finalDF, output], join='outer', ignore_index=True)
    else:
            DEGs = pd.read_csv(DEA_file, index_col=0)
            DEGs = DEGs.apply(lambda col:pd.to_numeric(col, errors='coerce'))
            samps = [c for c in DEGs.columns if 'log2FC' in c]
            samps = [s.replace("_log2FC", "") for s in samps]
            LFC_thresh = abs(L2FC_threshold)
            pval_thresh = abs(adjP_threshold)
            finalDF = pd.DataFrame()
            for i in samps:
                  cols = [c for c in DEGs.columns if i in c]
                  samp_DEG = DEGs[cols]
                  lfc_col = [c for c in samp_DEG.columns if 'log2FC' in c][0]
                  adjP_col =[c for c in samp_DEG.columns if 'Padj' in c][0]
                  samp_DEG = samp_DEG[samp_DEG[adjP_col] <  pval_thresh]
                  samp_DEG = samp_DEG[(samp_DEG[lfc_col] > LFC_thresh) | (samp_DEG[lfc_col] < (-LFC_thresh))]
                  genes = samp_DEG.index.to_list()
                  if org_name == 'mtruncatula':
                        genes = [s.replace('Medtr','MTR_') for s in genes]
                  gp = GProfiler(return_dataframe=True)
                  output = gp.profile(organism=org_name,
                              query= genes,
                              user_threshold=gProf_adjP_threshold)
                  output['Comparison'] = i
                  finalDF = pd.concat([finalDF, output], join='outer', ignore_index=True)
    finalDF.to_csv('Full_gProfiler.csv', index=False)

#This function will utilize the BP, MF, and CC output files generated by REVIGO
#in order to reduce the number of over-represented GO terms from the g:Profiler output
def combine_REVIGO_DEGs(gProfiler_output, revigo_BP, revigo_CC, revigo_MF):
      revigo_list = [revigo_BP, revigo_CC, revigo_MF]
      new_BP_name = revigo_BP.replace('.csv', '_output.csv')
      new_CC_name = revigo_CC.replace('.csv', '_output.csv')
      new_MF_name = revigo_MF.replace('.csv', '_output.csv')
      for i in revigo_list: #The goal of this loop is to correct for complex term names
            input_file = open(i, 'r') #that create issues for the pd.read_csv() import function
            outName = i.replace('.csv','_output.csv') 
            output_file = open(outName, 'w')
            checkWords = ("\",\"", "\", ")
            replaceWords = ('', '')
            for line in input_file:
                  for check, rep in zip(checkWords, replaceWords):
                        line = line.replace(check, rep)
                  output_file.write(line)
            input_file.close()
            output_file.close()
      BP_revigo = pd.read_csv(new_BP_name,quotechar='"',skipinitialspace=True)
      BP_revigo['source'] = 'GO:BP'
      CC_revigo = pd.read_csv(new_CC_name,quotechar='"',skipinitialspace=True)
      CC_revigo['source'] = 'GO:CC'
      MF_revigo = pd.read_csv(new_MF_name,quotechar='"',skipinitialspace=True)
      MF_revigo['source'] = 'GO:MF'
      full_gProfiler = pd.read_csv(gProfiler_output) 
      full_revigo = pd.concat([BP_revigo, CC_revigo, MF_revigo])
      full_revigo['Representative']= full_revigo['Representative'].fillna(0).astype(int).astype(str) #Corrects the GO term ID for adding to g:Profiler output
      full_revigo['Representative']= full_revigo['Representative'].str.rjust(7, "0")
      full_revigo['Representative']= 'GO:' + full_revigo['Representative'] 
      
                 
      GOnameDict = dict(zip(full_revigo['TermID'], full_revigo['Name']))
      sourceDict = dict(zip(full_revigo['TermID'], full_revigo['source']))

      newID = []
      for a, b, c in zip(full_revigo['TermID'], full_revigo['Representative'], 
                         full_revigo['Eliminated']):
            if c == False:
                  newID.append(a)
            elif c == True:
                  newID.append(b)

      full_revigo['NewID'] = newID
      reviGODict = dict(zip(full_revigo['TermID'], full_revigo['NewID']))
      
      full_gProfiler['native'] = full_gProfiler['native'].replace(reviGODict) #Renames g:Profiler output
      full_gProfiler['New Name'] = full_gProfiler['native'].map(GOnameDict)
      
      
      cleaned_Full = full_gProfiler.dropna(subset=['New Name']) #Removes duplicate GO term IDs from g:Profiler output
      
      cleaned_Full['source'] = cleaned_Full['native'].map(sourceDict)
      
      
      MF_subset = cleaned_Full[cleaned_Full['source']=='GO:MF'].drop_duplicates(subset=['New Name'])
      BP_subset = cleaned_Full[cleaned_Full['source']=='GO:BP'].drop_duplicates(subset=['New Name'])
      CC_subset = cleaned_Full[cleaned_Full['source']=='GO:CC'].drop_duplicates(subset=['New Name'])
      
      MF_subset.to_csv('MF_subset.csv', index=False)
      BP_subset.to_csv('BP_subset.csv', index=False)
      CC_subset.to_csv('CC_subset.csv', index=False)

#This function will plot either all of the REVIGO output files or the gProfiler output file
#This will generate 3 output files all .pdfs of the dotplot GO Enrichments
##NOTE: you must provide one of the following inputs for the function to run properly:
      #1) goEnrich_DotPlot(BP_enrich='someFile.csv', CC_enrich='someFile.csv', MF_enrich='someFile.csv')
      #2) goEnrich_DotPlot(full_gProfiler='someFile.csv')
##NOTE: if one or more of your REVIGO files is null, use a .csv with the REVIGO output headings
####### leave all values blank
def goEnrich_DotPlot(BP_enrich=None, CC_enrich=None, MF_enrich=None, 
                     adj_Pthresh=0.05, for_REVIGO=True, full_gProfiler=None, 
                     output_type='.pdf',
                     plot_width=8, plot_height=10,
                     subset_column_list=None):
      if for_REVIGO == True:
          if full_gProfiler is None:
              print('You need to add path for full_gProfiler file')
          full_Enrich = pd.read_csv(full_gProfiler)          
          BP = pd.read_csv(BP_enrich)
          CC = pd.read_csv(CC_enrich)
          MF = pd.read_csv(MF_enrich)
          #Modified for Revigo update
          BP['GeneRatio'] = BP['intersection_size'] / BP['term_size']
          CC['GeneRatio'] = CC['intersection_size'] / CC['term_size']
          MF['GeneRatio'] = MF['intersection_size'] / MF['term_size']

          #BP['GeneRatio'] = BP[' Frequency']
          #CC['GeneRatio'] = CC[' Frequency']
          #MF['GeneRatio'] = MF[' Frequency']
                  
          BP = BP.merge(full_Enrich, how='left', left_on='native', right_on='native')
          CC = CC.merge(full_Enrich, how='left', left_on='native', right_on='native')
          MF = MF.merge(full_Enrich, how='left', left_on='native', right_on='native')


      else:
            full_Enrich = pd.read_csv(full_gProfiler)
            full_Enrich['GeneRatio'] = full_Enrich['intersection_size'] / full_Enrich['term_size']
            full_Enrich['New Name'] = full_Enrich['name']
            BP = full_Enrich[full_Enrich['source'] == 'GO:BP']
            CC = full_Enrich[full_Enrich['source'] == 'GO:CC']
            MF = full_Enrich[full_Enrich['source'] == 'GO:MF']
#      return(BP)      
      BP = BP[BP['p_value_x'] <= adj_Pthresh]
      CC = CC[CC['p_value_x'] <= adj_Pthresh]
      MF = MF[MF['p_value_x'] <= adj_Pthresh]
      
      if subset_column_list is not None:
            BP = BP[subset_column_list]
            CC = CC[subset_column_list]
            MF = MF[subset_column_list]
                 
      hue = (adj_Pthresh/100, adj_Pthresh)
      
      f, ax = plt.subplots(figsize=(int(plot_width), int(plot_height)))
      sns.scatterplot(
          data=BP, x="Comparison_x", y="name_x", hue="p_value_x", 
          size="GeneRatio",
          sizes=(30, 300), hue_norm=hue, legend="brief", palette="YlOrBr_r")
      ax.set_ylabel('GO Term', size=14)
      plt.legend(loc='best')
      plt.title("Biological Process gProfiler Enrichment", size=18)
      plt.xticks(rotation=90)
      fileName = 'BP_enrich_dotplot' + output_type
      plt.savefig(fileName, bbox_inches='tight')
      
      f, ax = plt.subplots(figsize=(int(plot_width), int(plot_height)))
      sns.scatterplot(
          data=CC, x="Comparison_x", y="name_x", hue="p_value_x", 
          size="GeneRatio",
          sizes=(30, 300), hue_norm=hue, legend="brief", palette="YlOrBr_r")
      ax.set_ylabel('GO Term', size=14)
      plt.legend(loc='best')
      plt.title("Cellular Component gProfiler Enrichment", size=18)
      plt.xticks(rotation=90)
      fileName = 'CC_enrich_dotplot' + output_type
      plt.savefig(fileName, bbox_inches='tight')
      
      f, ax = plt.subplots(figsize=(int(plot_width), int(plot_height)))
      sns.scatterplot(
          data=MF, x="Comparison_x", y="name_x", hue="p_value_x", 
          size="GeneRatio",
          sizes=(30, 300), hue_norm=hue, legend="brief", palette="YlOrBr_r")
      ax.set_ylabel('GO Term', size=14)
      plt.legend(loc='best')
      plt.title("Molecular Function gProfiler Enrichment", size=18)
      plt.xticks(rotation=90)
      fileName = 'MF_enrich_dotplot' + output_type
      plt.savefig(fileName, bbox_inches='tight')
      

#goEnrich_DotPlot(BP_enrich='Sample Output/BP_subset.csv', CC_enrich='Sample Output/CC_subset.csv', MF_enrich='Sample Output/MF_subset.csv', 
#                     adj_Pthresh=0.01, output_type='.png')

#Function for running gProfiler on a file containing a list of genes categorized
#by modules
def run_gProfiler(DF, moduleList, org_name, verbose, custom_GMT=None, thresh=0.05, name=None):
      finalDF = pd.DataFrame()
      if name is not None:
            finalName = name + '_Full_gProfiler.csv'
      else:
            finalName = 'Full_gProfiler.csv'
      if custom_GMT is not None:
          with open(custom_GMT) as f:
              response = requests.post('https://biit.cs.ut.ee/gprofiler/api/gost/custom/',
                                       json={'gmt':f.read(),
                                             'name': custom_GMT})
              token = get_token_form_response(response)
              for i in moduleList:
                    newDf = DF[DF['Module']==i]
                    modGenes = newDf['index'].to_list()
              
                    gp = GProfiler(return_dataframe=True)
                    output = gp.profile(organism=token,
                                query= modGenes,
                                user_threshold=thresh)
                    name = i + '_gProfiler.csv'
                    output['Module'] = i
                    if verbose == True:
                          output.to_csv(name, index=False)
                    finalDF = pd.concat([finalDF, output], join='outer', ignore_index=True)
      else:
          for i in moduleList:
              newDf = DF[DF['Module']==i]
              modGenes = newDf['index'].to_list()
      
              gp = GProfiler(return_dataframe=True)
              output = gp.profile(organism=org_name,
                        query= modGenes,
                        user_threshold=thresh)
              name = i + '_gProfiler.csv'
              output['Module'] = i
              if verbose == True:
                    output.to_csv(name, index=False)
              finalDF = pd.concat([finalDF, output], join='outer', ignore_index=True) 
      finalDF.to_csv(finalName, index=False)

#This function takes the gene and module file outputs from WGCNA and performs a g:Profiler
#over-enrichment analysis in order to determine the over-enriched GO terms in 
#each co-expression module
##Optional arguments:
###gProf_adjP_threshold: a float that specifies the adj. P value cutoff for over-enriched pathway
###moduleRename_file: CSV File containing at least the following column names: "Module" and "Module_rename"
###This file should be used to rename the co-expression modules to a new system
###file_prefix: String that adds a prefix to the final output file
###verbose: Boolean (True/False). If True an individual g:Profiler output will be saved for every module
def gProfiler_WGCNA_modules(org_name, gene_mod_csv=None, gene_file=None, module_file=None, gProf_adjP_threshold=0.05, custom_GMT=None, moduleRename_file=None, file_prefix=None, verbose=False):
      if gene_mod_csv is None:
            Mods = pd.read_csv(module_file, sep='\t').T
            Genes = pd.read_csv(gene_file, sep='\t').T.reset_index()
            geneDF = pd.DataFrame(Genes['index'])
            geneDF['Module'] = Mods[1].to_list()
      else:
            geneDF = pd.DataFrame()
            modDF = pd.read_csv(gene_mod_csv)
            geneDF['index'] = modDF['A']
            geneDF['Module'] = modDF['B']
            Mods = geneDF
      if moduleRename_file is not None: #Need to fix the rename with file function
            moduleRename_DF = pd.read_csv(moduleRename_file)
            nameMapDict = dict(zip(moduleRename_DF['Module'], moduleRename_DF['Module_rename']))
      else:
            newName = []
            moduleRename_DF = Mods
            moduleRename_DF = moduleRename_DF.drop_duplicates(subset=['Module'])
            moduleRename_DF = moduleRename_DF.sort_values('Module')
            temp_Num = 1
            for i in moduleRename_DF['Module']:
                  temp_Name = 'Module_' + str(temp_Num)
                  newName.append(temp_Name)
                  temp_Num = temp_Num + 1
            moduleRename_DF['Module_rename'] = newName
            nameMapDict = dict(zip(moduleRename_DF['Module'], moduleRename_DF['Module_rename']))
            geneDF = geneDF.replace({'Module':nameMapDict})
      geneDF = geneDF[geneDF['Module'].str.contains('Module')]

      if org_name == 'mtruncatula':
            geneDF['index'] = geneDF['index'].str.replace('Medtr', 'MTR_')
      tempGenes = geneDF.drop_duplicates(subset=['Module'])
      gene_Mods = tempGenes['Module'].to_list()
      geneDF.to_csv('output.csv')
      run_gProfiler(geneDF, gene_Mods, org_name=org_name, custom_GMT=custom_GMT, name=file_prefix, verbose=verbose)
#      geneDF.to_csv('output.csv')

def combine_REVIGO_Modules(gProfiler_output, revigo_BP, revigo_CC, revigo_MF):
      revigo_list = [revigo_BP, revigo_CC, revigo_MF]
      new_BP_name = revigo_BP.replace('.csv', '_output.csv')
      new_CC_name = revigo_CC.replace('.csv', '_output.csv')
      new_MF_name = revigo_MF.replace('.csv', '_output.csv')
      for i in revigo_list: #The goal of this loop is to correct for complex term names
            input_file = open(i, 'r') #that create issues for the pd.read_csv() import function
            outName = i.replace('.csv','_output.csv') 
            output_file = open(outName, 'w')
            checkWords = ("\",\"", "\", ")
            replaceWords = ('', '')
            for line in input_file:
                  for check, rep in zip(checkWords, replaceWords):
                        line = line.replace(check, rep)
                  output_file.write(line)
            input_file.close()
            output_file.close()
      BP_revigo = pd.read_csv(new_BP_name,quotechar='"',skipinitialspace=True)
      CC_revigo = pd.read_csv(new_CC_name,quotechar='"',skipinitialspace=True)
      MF_revigo = pd.read_csv(new_MF_name,quotechar='"',skipinitialspace=True)
      full_gProfiler = pd.read_csv(gProfiler_output) 
      full_revigo = pd.concat([BP_revigo, CC_revigo, MF_revigo])
      full_revigo['Representative']= full_revigo['Representative'].fillna(0).astype(int).astype(str) #Corrects the GO term ID for adding to g:Profiler output
      full_revigo['Representative']= full_revigo['Representative'].str.rjust(7, "0")
      full_revigo['Representative']= 'GO:' + full_revigo['Representative'] 
                 
      GOnameDict = dict(zip(full_revigo['TermID'], full_revigo['Name']))

      newID = []
      for a, b, c in zip(full_revigo['TermID'], full_revigo['Representative'], 
                         full_revigo['Eliminated']):
            if c == False:
                  newID.append(a)
            elif c == True:
                  newID.append(b)

      full_revigo['NewID'] = newID
      return full_revigo
      reviGODict = dict(zip(full_revigo['TermID'], full_revigo['NewID']))
      
      full_gProfiler['native'] = full_gProfiler['native'].replace(reviGODict) #Renames g:Proviler output
      full_gProfiler['New Name'] = full_gProfiler['native'].map(GOnameDict)
      
      cleaned_Full = full_gProfiler.dropna(subset=['New Name']) #Removes duplicate GO term IDs from g:Profiler output
      
      MF_subset = cleaned_Full[cleaned_Full['source']=='GO:MF'].drop_duplicates(subset=['New Name'])
      BP_subset = cleaned_Full[cleaned_Full['source']=='GO:BP'].drop_duplicates(subset=['New Name'])
      CC_subset = cleaned_Full[cleaned_Full['source']=='GO:CC'].drop_duplicates(subset=['New Name'])
      
      MF_crosstab = pd.crosstab(MF_subset['Module'], MF_subset['New Name'])
      BP_crosstab = pd.crosstab(BP_subset['Module'], BP_subset['New Name'])
      CC_crosstab = pd.crosstab(CC_subset['Module'], CC_subset['New Name'])
      
      MF_crosstab.to_csv('MF_subset.csv')
      BP_crosstab.to_csv('BP_subset.csv')
      CC_crosstab.to_csv('CC_subset.csv')
      
def plot_module_DEG_Heatmap(DEG_file, WGCNA_output_genes_file, 
                            WGCNA_output_modules_file, 
                            L2FC_threshold=1.0, p_adj_threshold=0.05,
                            moduleRename_file=None,
                            subset_list=None):
      def removeNanFromDict(Dict):
            tempDict = {}
            for key, value in Dict.items():
                  newVals = [x for x in value if str(x) != 'nan']
                  tempDict[key] = newVals
            return tempDict
      
      def convertValsTolist(Dict):
            finalDict = {}
            for key, value in Dict.items():
                  finalDict[key] = value.split(',')
            return finalDict
      
      def grabSig(DF, L2FC=1.0, p_adj=0.05):
            cols = [c for c in DF.columns if '_padj' in c]
            padj = DF[cols]
            tempIndex = list(padj.min(axis=1).reset_index().columns)[0]
            minValIndex = padj.min(axis=1).reset_index().set_index(tempIndex).rename(columns={0:'minPadj'})
            cols = [c for c in DF.columns if '_log2FoldChange' in c]
            lfc = DF[cols]
            maxlfcValIndex = lfc.max(axis=1).reset_index().set_index(tempIndex).rename(columns={0:'maxLFC'})
            minlfcValIndex = lfc.min(axis=1).reset_index().set_index(tempIndex).rename(columns={0:'minLFC'})
            DF = DF.merge(minValIndex, how='outer', left_index=True, right_index=True)
            DF = DF.merge(maxlfcValIndex, how='outer', left_index=True, right_index=True)
            DF = DF.merge(minlfcValIndex, how='outer', left_index=True, right_index=True)
            Cleaned = DF[DF['minPadj'] < p_adj]
            newClean = Cleaned[(Cleaned['maxLFC'] >= abs(L2FC)) | (Cleaned['minLFC'] <= -abs(L2FC))]
            return newClean
      
      def removeUnwantedLFCs(DF, L2FC=1.0, p_adj=0.05):
            lfc_cols = [c for c in DF.columns if '_log2FoldChange' in c]
            padj_cols = [c for c in DF.columns if '_padj' in c]
            newSig =DF[['index', 'Module']]
            for a, b in zip(lfc_cols, padj_cols):
                  newI = []
                  for i, j in zip(DF[a], DF[b]):
                        if j > p_adj:
                              z = np.nan
                        elif abs(L2FC) > i > -abs(L2FC):
                              z = np.nan
                        else:
                              z = i            
                        newI.append(z)
                  newSig[a] = newI
            return newSig
      
      DEGs = pd.read_csv(DEG_file)
      Mods = pd.read_csv(WGCNA_output_modules_file, sep='\t').T
      Genes = pd.read_csv(WGCNA_output_genes_file, sep='\t').T.reset_index()
      
      new_DEGs = pd.DataFrame(Genes['index'])
      new_DEGs['Module'] = Mods[1].to_list()
      new_DEGs = new_DEGs.merge(DEGs, how='left', left_on='index', right_on='Gene').drop(columns=['Gene'])
      
      if moduleRename_file is not None:
            moduleRename_DF = pd.read_csv(moduleRename_file)
            nameMapDict = dict(zip(moduleRename_DF['Module'], moduleRename_DF['Module_rename']))
      else:
            newName = []
            moduleRename_DF = Mods
            moduleRename_DF = moduleRename_DF.drop_duplicates(subset=[1])
            moduleRename_DF = moduleRename_DF.sort_values(1)
            temp_Num = 1
            for i in moduleRename_DF[1]:
                  temp_Name = 'Module_' + str(temp_Num)
                  newName.append(temp_Name)
                  temp_Num = temp_Num + 1
            moduleRename_DF['Module_rename'] = newName
            nameMapDict = dict(zip(moduleRename_DF[1], moduleRename_DF['Module_rename'])) 
      
      new_DEGs = new_DEGs.reset_index()
      
      new_DEGs = new_DEGs.replace({'Module':nameMapDict})
            
      DEG_sig = grabSig(new_DEGs, L2FC=L2FC_threshold, p_adj=p_adj_threshold)

      DEG_for_avg = removeUnwantedLFCs(DEG_sig, L2FC=L2FC_threshold, p_adj=p_adj_threshold)
      
      lfc_cols = [c for c in DEG_for_avg.columns if '_log2FoldChange' in c]
      for_Heat = pd.pivot_table(DEG_for_avg, index='Module',values=lfc_cols, aggfunc=np.mean)
      
      if subset_list is not None:
            for_Heat = for_Heat[subset_list]
            
      for_Heat.to_csv('For Co-expression Module Heatmap.csv')

def plot_Genes_of_interest(normCounts_file, metaData_file, genesOfInterest_file, treatment_column, sort_order, subset=None):
      finalDF = pd.read_csv(normCounts_file, index_col=0).T
      metaDF = pd.read_csv(metaData_file).set_index('Samples')
      tempMeta = metaDF[treatment_column]
      
      calcDF = pd.concat([finalDF, tempMeta], join='outer', axis=1, sort=False)
      
      genes = pd.read_csv(genesOfInterest_file, header=None)
      geneList = genes[0].to_list()
      
      subset = calcDF[geneList]
      subset = subset.merge(metaDF[treatment_column], how='left', left_index=True, right_index=True)
      
      calcDF2 = subset.groupby([treatment_column]).describe()
      calcDF3 = calcDF2
      calcDF3.columns = calcDF3.columns.map('_'.join).str.strip('_')
      
      mean = calcDF3.filter(regex='mean').reset_index()
      std = calcDF3.filter(regex='std').reset_index()
      
      mean = mean[mean['StrainXTreatmentXTissue'].str.contains('Root')].set_index('StrainXTreatmentXTissue')

      control = []
      for i in mean.index:
            if 'Control' in i:
                  control.append('Control')
            elif 'CdTreated' in i:
                  control.append('Cd_Treated')
            elif 'HgTreated' in i:
                  control.append('Hg_Treated')
      mean['Control'] = control
      mean_forHeatMap = mean.drop(columns=['Control'])
      Zscore = stats.zscore(mean_forHeatMap)
      HeatmapFinal = pd.DataFrame(Zscore)
      HeatmapFinal.index = mean_forHeatMap.index
      HeatmapFinal.columns = mean_forHeatMap.columns
      HeatmapFinal.to_csv('For Genes of Interest Heatmap2.csv')
      Std = std[std['StrainXTreatmentXTissue'].str.contains('Root')].set_index('StrainXTreatmentXTissue')
          
      mean = mean.reindex(sort_order)
      
      for i in mean.columns:
            fig, ax = plt.subplots()
            name = 'MOD31/' + i + '.pdf'
            g = sns.barplot(x=mean.index, y=i, hue="Control",\
                            data=mean)
            plt.xticks(rotation=90)
            plt.ylabel('Mean TPM')
            plt.title(i)
            plt.tight_layout()
            
            plt.savefig(name, dpi=300)
            plt.show()

      
#rootSort = ['HM075_Control_Root', 'HM075_CdTreated_Root',  'HM195_Control_Root', 
#            'HM195_CdTreated_Root', 'HM302_Control_Root', 'HM302_HgTreated_Root',
#       'HM304_Control_Root', 'HM304_HgTreated_Root','PI660407_Control_Root', 
#       'PI660407_CdTreated_Root', 'PI660407_HgTreated_Root']

#leafSort = ['HM001_Control_Leaf', 'HM001_CdTreated_Leaf','HM075_Control_Leaf','HM075_CdTreated_Leaf',
#       'HM176_Control_Leaf','HM176_CdTreated_Leaf','HM178_Control_Leaf', 'HM178_HgTreated_Leaf',
#       'HM195_Control_Leaf', 'HM195_CdTreated_Leaf','HM238_Control_Leaf', 'HM238_HgTreated_Leaf',
#       'HM302_Control_Leaf', 'HM302_HgTreated_Leaf', 'HM304_Control_Leaf',
#       'HM304_HgTreated_Leaf', 'PI660407_Control_Leaf', 'PI660407_CdTreated_Leaf',
#        'PI660407_HgTreated_Leaf']
      
#plot_Genes_of_interest(normCounts_file='All TPM Counts.csv', 
#                       metaData_file='allMetadata.csv', 
#                       genesOfInterest_file='subset of module 31.csv',
#                       treatment_column='StrainXTreatmentXTissue',
#                       sort_order=rootSort,
#                       subset='Root')   

