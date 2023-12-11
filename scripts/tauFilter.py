import ROOT
import numpy as np
import glob
import sys, argparse

ROOT.EnableImplicitMT(8)

RDataFrame = ROOT.RDataFrame
inputFiles = ['/media/DATA2/NANO_DATA/2023/JetMET0_Run2023C-22Sep2023_v4-v1_NANOAOD/000ddcf4-658b-42c8-a742-bbcf7060f1ab.root']
outputFile = 'output'

    
def getOptions():
    parser = argparse.ArgumentParser(description="Run a simple dijet analysis on nanoAOD with RDataFrames")
    parser.add_argument("-f_in", "--inputFiles", type=str, default=inputFiles, nargs='+', help="Input files separated by a comma")
    parser.add_argument("-o", "--outputFile", type=str, default=outputFile, help="Output file name")
    return parser.parse_args()
    
    
def strTakeN(colName, n):
    result = ""
    
    # Loop over the range of n and add the Take function to the result
    for i in range(n, 1, -1):
        result += f"{colName}.size() > {i-1} ? ROOT::VecOps::Take({colName}, {i}) : ("
        
    # Add the last Take function to the result
    result += f"ROOT::VecOps::Take({colName}, 1)" + ")"*(n-1)
    
    return result
    

if __name__ == "__main__":
    # Get command line arguments
    args = getOptions()

    filepath = args.filepath
    inputFiles = args.inputFiles# .split(",")
    outputFile = args.outputFile
    
    # Columns to analyze and use
    # cols = ["Jet_pt"]
    
    chain = ROOT.TChain("Events")
    for file in inputFiles:
        chain.Add(file)
        
    # chain.Add(inputFiles[0])    
    # Create RDataFrame
    rdf = RDataFrame(chain)
    # df = makeRDF(inputFiles)
    print("Filtering events")
    # Filter jets
    rdf = (rdf.Filter("Jet_pt.size() > 2", "Filter events with at least 3 jets")
            .Filter("(Jet_pt[0] + Jet_pt[1]) / 2.0 > Jet_pt[2]", "Choose dijet events")
        )

    # Print the number of events
    print("Number of events:")
    print(rdf.Count().GetValue())
    
    # Plot jet_pt
    h_jet_pt = rdf.Histo1D(("Jet_pt", "Jet_pt", 100, 0, 1000), "Jet_pt")
    
    # Write the histogram to a file
    print("Writing histogram to file")
    f = ROOT.TFile.Open(outputFile+".root", "RECREATE")
    h_jet_pt.Write()
    f.Close()