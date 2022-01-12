#=====================================================================================
#
#  Code chunk 1
#
#=====================================================================================


# Display the current working directory
dir <- getwd()
setwd(dir)

# Load the WGCNA package
library(WGCNA);
# The following setting is important, do not omit.
options(stringsAsFactors = FALSE);
#Read in the female liver data set
#Read in the female liver data set
femData = read.csv("All_Medicago_Counts.csv");
# Take a quick look at what is in the data set:
#dim(femData);
#names(femData);
femMeta = read.csv("allMetadata.csv")
femMeta = femMeta[ which(femMeta$TissueType=='Leaf'), ]
sampList = femMeta$Samples
sampList = c("Gene", sampList)
femData = femData[ , sampList]


#=====================================================================================
#
#  Code chunk 2
#
#=====================================================================================


datExpr0 = as.data.frame(t(femData[, -c(1)]));
names(datExpr0) = femData$Gene;
rownames(datExpr0) = names(femData)[-c(1)];
#dim(datExpr0)
print("printing rownames")
print(rownames(datExpr0))

#=====================================================================================
#
#  Code chunk 3
#
#=====================================================================================


gsg = goodSamplesGenes(datExpr0, verbose = 3);
gsg$allOK


#=====================================================================================
#
#  Code chunk 4
#
#=====================================================================================


if (!gsg$allOK)
{
  # Optionally, print the gene and sample names that were removed:
  if (sum(!gsg$goodGenes)>0) 
    printFlush(paste("Removing genes:", paste(names(datExpr0)[!gsg$goodGenes], collapse = ", ")));
  if (sum(!gsg$goodSamples)>0) 
    printFlush(paste("Removing samples:", paste(rownames(datExpr0)[!gsg$goodSamples], collapse = ", ")));
  # Remove the offending genes and samples from the data:
  datExpr0 = datExpr0[gsg$goodSamples, gsg$goodGenes]
}


#=====================================================================================
#
#  Code chunk 5
#
#=====================================================================================


sampleTree = hclust(dist(datExpr0), method = "average");
# Plot the sample tree: Open a graphic output window of size 12 by 9 inches
# The user should change the dimensions if the window is too large or too small.
sizeGrWindow(12,9)
pdf(file = "Plots/Leaf_PlantsampleClustering.pdf", width = 12, height = 9);
par(cex = 0.6);
par(mar = c(0,4,2,0))
plot(sampleTree, main = "Plant_Sample clustering to detect outliers", sub="", xlab="", cex.lab = 1.5, 
     cex.axis = 1.5, cex.main = 2)


#=====================================================================================
#
#  Code chunk 6
#
#=====================================================================================


# Plot a line to show the cut
abline(h = 280, col = "red");
# Determine cluster under the line
clust = cutreeStatic(sampleTree, cutHeight = 150, minSize = 10)
table(clust)
# clust 1 contains the samples we want to keep.
keepSamples = (clust==1)
datExpr = datExpr0[keepSamples, ]
nGenes = ncol(datExpr)
nSamples = nrow(datExpr)
dev.off()

#=====================================================================================
#
#  Code chunk 7
#
#=====================================================================================


#traitData = read.csv("WGCNA counts PlantMeta2.csv");
#dim(traitData)
#names(traitData)

# remove columns that hold information we do not need.
#allTraits = traitData[, -c(6, 7)];
#allTraits = allTraits[, c(2, 11:36) ];
#dim(allTraits)
#names(allTraits)

# Form a data frame analogous to expression data that will hold the clinical traits.

#femaleSamples = rownames(datExpr);
#traitRows = match(femaleSamples, allTraits$File);
#datTraits = allTraits[traitRows, -1];
#rownames(datTraits) = allTraits[traitRows, 1];

#collectGarbage();


#=====================================================================================
#
#  Code chunk 8
#
#=====================================================================================


# Re-cluster samples
#sampleTree2 = hclust(dist(datExpr), method = "average")
# Convert traits to a color representation: white means low, red means high, grey means missing entry
#traitColors = numbers2colors(datTraits, signed = FALSE);
# Plot the sample dendrogram and the colors underneath.
#plotDendroAndColors(sampleTree2, traitColors,
#                    groupLabels = names(datTraits), 
#                    main = "Sample dendrogram and trait heatmap")


#=====================================================================================
#
#  Code chunk 9
#
#=====================================================================================


save(datExpr, file = "Leaf-01-dataInput.RData")

############################################################################
#Step-by-step network construction
#=====================================================================================
#
#  Code chunk 1
#
#=====================================================================================


# Display the current working directory
dir <- getwd()
setwd(dir)

# The following setting is important, do not omit.
options(stringsAsFactors = FALSE);
# Allow multi-threading within WGCNA. At present this call is necessary.
# Any error here may be ignored but you may want to update WGCNA if you see one.
# Caution: skip this line if you run RStudio or other third-party R environments.
# See note above.
enableWGCNAThreads()
# Load the data saved in the first part
lnames = load(file = "Leaf-01-dataInput.RData");
#The variable lnames contains the names of loaded variables.
lnames


#=====================================================================================
#
#  Code chunk 2
#
#=====================================================================================


# Choose a set of soft-thresholding powers
powers = c(c(1:10), seq(from = 12, to=30, by=2))
# Call the network topology analysis function
sft = pickSoftThreshold(datExpr, powerVector = powers, verbose = 5)
# Plot the results:
sizeGrWindow(9, 5)
par(mfrow = c(1,2));
cex1 = 0.9;
pdf(file = "Plots/Leaf_SoftThresholdvScaleFreeToplogy.pdf", width = 12, height = 9);
# Scale-free topology fit index as a function of the soft-thresholding power
plot(sft$fitIndices[,1], -sign(sft$fitIndices[,3])*sft$fitIndices[,2],
     xlab="Soft Threshold (power)",ylab="Scale Free Topology Model Fit,signed R^2",type="n",
     main = paste("Scale independence"));
text(sft$fitIndices[,1], -sign(sft$fitIndices[,3])*sft$fitIndices[,2],
     labels=powers,cex=cex1,col="red");
# this line corresponds to using an R^2 cut-off of h
abline(h=0.90,col="red")
dev.off()
pdf(file = "Plots/Leaf_SoftThresholdvsMeanConnectivity.pdf", width = 12, height = 9);
# Mean connectivity as a function of the soft-thresholding power
plot(sft$fitIndices[,1], sft$fitIndices[,5],
     xlab="Soft Threshold (power)",ylab="Mean Connectivity", type="n",
     main = paste("Mean connectivity"))
text(sft$fitIndices[,1], sft$fitIndices[,5], labels=powers, cex=cex1,col="red")
dev.off()

#=====================================================================================
#
#  Code chunk 3
#
#=====================================================================================


softPower = 8;
adjacency = adjacency(datExpr, power = softPower);


#=====================================================================================
#
#  Code chunk 4
#
#=====================================================================================


# Turn adjacency into topological overlap
TOM = TOMsimilarity(adjacency);
dissTOM = 1-TOM

save(dissTOM, file = "Leaf-01-dissTOM.RData")
#=====================================================================================
#
#  Code chunk 5
#
#=====================================================================================


# Call the hierarchical clustering function
geneTree = hclust(as.dist(dissTOM), method = "average");
# Plot the resulting clustering tree (dendrogram)
sizeGrWindow(12,9)
pdf(file = "Plots/Leaf_Gene Clustering.pdf", width = 12, height = 9);
plot(geneTree, xlab="", sub="", main = "Gene clustering on TOM-based dissimilarity",
     labels = FALSE, hang = 0.04);

#=====================================================================================
#
#  Code chunk 6
#
#=====================================================================================


# We like large modules, so we set the minimum module size relatively high:
minModuleSize = 30;
# Module identification using dynamic tree cut:
dynamicMods = cutreeDynamic(dendro = geneTree, distM = dissTOM,
                            deepSplit = 2, pamRespectsDendro = FALSE,
                            minClusterSize = minModuleSize);
table(dynamicMods)
dev.off()

#=====================================================================================
#
#  Code chunk 7
#
#=====================================================================================


# Convert numeric lables into colors
dynamicColors = labels2colors(dynamicMods)
table(dynamicColors)
# Plot the dendrogram and colors underneath
pdf(file = "Plots/Leaf_Gene Dendogram with module colors.pdf", width = 12, height = 9);
sizeGrWindow(8,6)
plotDendroAndColors(geneTree, dynamicColors, "Dynamic Tree Cut",
                    dendroLabels = FALSE, hang = 0.03,
                    addGuide = TRUE, guideHang = 0.05,
                    main = "Gene dendrogram and module colors")
dev.off()

#=====================================================================================
#
#  Code chunk 8
#
#=====================================================================================


# Calculate eigengenes
MEList = moduleEigengenes(datExpr, colors = dynamicColors)
MEs = MEList$eigengenes
# Calculate dissimilarity of module eigengenes
MEDiss = 1-cor(MEs, use="pairwise.complete.obs");
# Cluster module eigengenes
METree = hclust(as.dist(MEDiss), method = "average");
# Plot the result
pdf(file = "Plots/Leaf_ClusterinfofModuleEigengenes.pdf", width = 12, height = 9);
sizeGrWindow(7, 6)
plot(METree, main = "Clustering of module eigengenes",
     xlab = "", sub = "")

#=====================================================================================
#
#  Code chunk 9
#
#=====================================================================================


MEDissThres = 0.25
# Plot the cut line into the dendrogram
abline(h=MEDissThres, col = "red")
# Call an automatic merging function
merge = mergeCloseModules(datExpr, dynamicColors, cutHeight = MEDissThres, verbose = 3)
# The merged module colors
mergedColors = merge$colors;
# Eigengenes of the new merged modules:
mergedMEs = merge$newMEs;
dev.off()

#=====================================================================================
#
#  Code chunk 10
#
#=====================================================================================


sizeGrWindow(12, 9)
pdf(file = "Plots/Leaf_geneDendro-3.pdf", wi = 9, he = 6)
plotDendroAndColors(geneTree, cbind(dynamicColors, mergedColors),
                    c("Dynamic Tree Cut", "Merged dynamic"),
                    dendroLabels = FALSE, hang = 0.03,
                    addGuide = TRUE, guideHang = 0.05)
dev.off()


#=====================================================================================
#
#  Code chunk 11
#
#=====================================================================================


# Rename to moduleColors
moduleColors = mergedColors
# Construct numerical labels corresponding to the colors
colorOrder = c("grey", standardColors(50));
moduleLabels = match(moduleColors, colorOrder)-1;
MEs = mergedMEs;

#####################################################################################
#for cytoscape export
annot = read.csv("All_Medicago_Counts.csv");

#select modules
modules = moduleColors

#select probes
probes = names(datExpr);

inModule = (moduleColors==modules);
modProbes = probes[inModule];
modGenes = annot$Gene[match(modProbes, annot$Gene)];

modTOM = TOM[inModule, inModule];
dimnames(modTOM) = list(modProbes, modProbes)

cyt = exportNetworkToCytoscape(modTOM,
                               edgeFile=paste("Leaf_CytoEdge_allMods", ".txt", sep=""),
                               nodeFile=paste("Leaf_Node_allMods", ".txt", sep=""),
                               weighted=TRUE, threshold=0.02, nodeNames=modProbes, altNodeNames=modGenes, nodeAttr=moduleColors[inModule])
# Save module colors and labels for use in subsequent parts
save(MEs, moduleLabels, moduleColors, geneTree, file = "Leaf-02-networkConstruction-stepByStep.RData")

