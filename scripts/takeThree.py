import ROOT
import argparse

inputFile = "/media/storage/nicotoik/tauFilter/output/19Dec2023/Run2023C_taus.root"
outputFile = "/media/storage/nicotoik/tauFilter/output/19Dec2023/Run2023C_jets.root"

def getOptions():
    parser = argparse.ArgumentParser(description="Read in a ROOT file and skim it to three leading jets")
    parser.add_argument("-f_in", "--inputFiles", type=str, default=inputFile, nargs='+', help="Input file")
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
    args = getOptions()

    inputFile = args.inputFiles
    outputFile = args.outputFile
    
    rdf = ROOT.RDataFrame("Events", inputFile)
    
    Jet_cols = ["Jet_eta", "Jet_phi", "Jet_pt", "Jet_mass", "Jet_jetId", "Jet_nConstituents", "Jet_rawFactor"]
    
    ROOT.gInterpreter.Declare("""
std::vector<Float_t> RVectoStdVector(const ROOT::RVec<Float_t>& rvec) {
    std::vector<Float_t> result;
    result.reserve(rvec.size()); // Reserve memory for efficiency

    for (const auto& element : rvec) {
        result.push_back(element);
    }
    
    return result;
}
                              """)

    for col in Jet_cols:
        rdf = rdf.Redefine(col, strTakeN(col, 3)).Redefine(col, f"RVectoStdVector({col})")
    
    print("Writing to file...")
    rdf.Snapshot("Events", outputFile)
    print("Done!")