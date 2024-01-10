import ROOT
import numpy as np
import glob
import sys, argparse

ROOT.EnableImplicitMT(32)

RDataFrame = ROOT.RDataFrame
inputFiles = ['/media/DATA/NANO_DATA/2023/JetMET0_Run2023C-PromptNanoAODv11p9_v1-v1_NANOAOD/a5a36540-67cd-4853-920a-e55c3c1bcb47.root']
outputFile = 'output'

def getOptions():
    parser = argparse.ArgumentParser(description="Run a tau filter on Run 3 data")
    parser.add_argument("-f_in", "--inputFiles", type=str, default=inputFiles, nargs='+', help="Input files separated by a comma")
    parser.add_argument("-o", "--outputFile", type=str, default=outputFile, help="Output file name")
    parser.add_argument("-IOV", "--IOV", type=str, default="2023Cv123", help="IOV of the JEC to use")
    return parser.parse_args()

if __name__ == "__main__":

    # Get command line arguments
    args = getOptions()

    inputFiles = args.inputFiles
    outputFile = args.outputFile
    IOV = args.IOV
    
    print(f"Loading {len(inputFiles)} files")
    chain = ROOT.TChain("Events")
    for file in inputFiles:
        chain.Add(file)
        
    # Create RDataFrame
    rdf = RDataFrame(chain)
    print("RDF created")
    
    # Filter good vertices
    rdf = rdf.Filter("PV_npvsGood > 0", "Good vertices")
    
    # Find the smallest and largest run numbers
    # Min: 366403, Max: 370790
    min_run = 366403 # rdf.Min("run")
    max_run = 370790 # rdf.Max("run")
    
    # Create an integer binning for the run numbers
    run_bins = np.arange(min_run, max_run, 1, dtype=float)
    
    print(f"Run range: {min_run} - {max_run}")
    
    # Create a binning for Bundh Crossing
    bx_bins = np.arange(0, 3565, 1, dtype=float)
    
    # Simple map, no cuts
    h = rdf.Histo2D(("simpleMap", "Simple map;Run;BX", len(run_bins) - 1, run_bins, len(bx_bins) - 1, bx_bins), "run", "bunchCrossing")     
    
    # Write the output
    f = ROOT.TFile(outputFile + ".root", "RECREATE")
    h.Write()
    f.Close()