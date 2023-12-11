import ROOT
import numpy as np
import glob
import sys, argparse

ROOT.EnableImplicitMT(16)

RDataFrame = ROOT.RDataFrame
inputFiles = ['/media/DATA/NANO_DATA/2023/JetMET0_Run2023C-PromptNanoAODv11p9_v1-v1_NANOAOD/a5a36540-67cd-4853-920a-e55c3c1bcb47.root']
outputFile = 'output'

    
def getOptions():
    parser = argparse.ArgumentParser(description="Run a tau filter on Run 3 data")
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

    inputFiles = args.inputFiles
    outputFile = args.outputFile

    print(f"Loading {len(inputFiles)} files")
    chain = ROOT.TChain("Events")
    for file in inputFiles:
        chain.Add(file)
        
    selected_columns = ["L1Tau_hwIso", "L1Tau_bx", "L1Tau_eta", "L1Tau_phi", "L1Tau_pt", "HLT_PFJet500"]  
    # Create RDataFrame
    rdf = RDataFrame(chain, selected_columns)
    print("RDF created")
    
    # Filter jets
    print("Filtering events")
    rdf = (rdf.Filter("HLT_PFJet500", "Filter events with HLT_PFJet500")
        )

    # Print the number of events
    print("Number of events:")
    print(rdf.Count().GetValue())
    
    # Write the dataframe to a ROOT file
    print(f"Writing dataframe to file {outputFile}.root")
    rdf.Snapshot("Events", outputFile+".root", selected_columns)
    