import ROOT
import numpy as np
import glob
import sys, argparse

# Load the libraries for JEC
ROOT.gSystem.Load("../JetMETObjects/src/FactorizedJetCorrector_cc.so")
ROOT.gSystem.Load("../JetMETObjects/src/JetCorrectionUncertainty_cc.so")
ROOT.gSystem.Load("../JetMETObjects/src/JetCorrectorParameters_cc.so")
ROOT.gSystem.Load("../JetMETObjects/src/JetResolutionObject_cc.so")
ROOT.gSystem.Load("../JetMETObjects/src/SimpleJetCorrector_cc.so")
ROOT.gSystem.Load("../JetMETObjects/src/SimpleJetCorrectionUncertainty_cc.so")
"""
ROOT.gSystem.Load("../JetMETObjects/src/FactorizedJetCorrector.cc")
ROOT.gSystem.Load("../JetMETObjects/src/JetCorrectionUncertainty.cc")
ROOT.gSystem.Load("../JetMETObjects/src/JetCorrectorParameters.cc")
ROOT.gSystem.Load("../JetMETObjects/src/JetResolutionObject.cc")
ROOT.gSystem.Load("../JetMETObjects/src/SimpleJetCorrector.cc")
ROOT.gSystem.Load("../JetMETObjects/src/SimpleJetCorrectionUncertainty.cc")
"""
# Headers for declaring the JEC and JER objects
ROOT.gInterpreter.Declare("""
#include "../JetMETObjects/interface/FactorizedJetCorrector.h"
#include "../JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "../JetMETObjects/interface/JetCorrectorParameters.h"
#include "../JetMETObjects/interface/JetResolutionObject.h"
#include "../JetMETObjects/interface/SimpleJetCorrector.h"
#include "../JetMETObjects/interface/SimpleJetCorrectionUncertainty.h"
""")


ROOT.EnableImplicitMT(32)

RDataFrame = ROOT.RDataFrame
inputFiles = ['/media/DATA/NANO_DATA/2023/JetMET0_Run2023C-PromptNanoAODv11p9_v1-v1_NANOAOD/a5a36540-67cd-4853-920a-e55c3c1bcb47.root']
outputFile = 'output'

# Dictionary of IOV to JEC object
JEC_dict = {"2023B" : "Summer22Prompt23_Run2023Cv123_V3_DATA",
            "2023Cv123" : "Summer22Prompt23_Run2023Cv123_V3_DATA",
            "2023Cv4" : "Summer22Prompt23_Run2023Cv4_V3_DATA",
            "2023D" : "Summer22Prompt23_Run2023D_V3_DATA"}

def getOptions():
    parser = argparse.ArgumentParser(description="Run a tau filter on Run 3 data")
    parser.add_argument("-f_in", "--inputFiles", type=str, default=inputFiles, nargs='+', help="Input files separated by a comma")
    parser.add_argument("-o", "--outputFile", type=str, default=outputFile, help="Output file name")
    parser.add_argument("-IOV", "--IOV", type=str, default="2023Cv123", help="IOV of the JEC to use")
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
    IOV = args.IOV
    
    CorrectionSet = JEC_dict[IOV]
    print(f"Using {CorrectionSet} JEC")
    ROOT.gInterpreter.Declare("""
                        #ifndef JEC_CODE
                        #define JEC_CODE
                        
                        JetCorrectorParameters *L2Relative;
                        JetCorrectorParameters *L2L3Residual;
                        
                        std::vector<JetCorrectorParameters> correctionParameters;
                        
                        void initJEC() {
                            const char* L2RelativeFile = Form("../JetMETObjects/data/Summer22Run3_V1_MC_L2Relative_AK4PUPPI.txt");
                            const char* L2L3ResidualFile = Form("../JetMETObjects/data/""" + CorrectionSet + """_L2L3Residual_AK4PFPUPPI.txt");
                            
                            JetCorrectorParameters *L2Relative = new JetCorrectorParameters(L2RelativeFile);
                            JetCorrectorParameters *L2L3Residual = new JetCorrectorParameters(L2L3ResidualFile);
                            
                            correctionParameters.push_back(*L2Relative);
                            correctionParameters.push_back(*L2L3Residual);
                        }
                        
                        ROOT::RVec<Float_t> CorrectedJetPt(unsigned int slot, ULong64_t entry, ROOT::RVec<Float_t> JetPt, ROOT::RVec<Float_t> JetEta, ROOT::RVec<Float_t> JetArea, Float_t Rho) {
                            std::unique_ptr<FactorizedJetCorrector> JetCorrector;
                            ROOT::RVec<Float_t> CorrectedJetPt(JetPt.size());

                            JetCorrector = std::make_unique<FactorizedJetCorrector>(correctionParameters);

                            for (size_t i = 0; i < JetPt.size(); i++) {
                                JetCorrector->setJetPt(JetPt[i]);
                                JetCorrector->setJetEta(JetEta[i]);
                                JetCorrector->setJetA(JetArea[i]);
                                JetCorrector->setRho(Rho);
                                CorrectedJetPt[i] = JetCorrector->getCorrection();
                            }

                            return CorrectedJetPt;
                        }
                        
                        #endif
                        """)
    
    ROOT.initJEC()

    print(f"Loading {len(inputFiles)} files")
    chain = ROOT.TChain("Events")
    for file in inputFiles:
        chain.Add(file)
        
    # L1 columns
    L1_cols = ["L1Tau_hwIso", "L1Tau_bx", "L1Tau_eta", "L1Tau_phi", "L1Tau_pt",
               "L1Jet_bx", "L1Jet_eta", "L1Jet_phi", "L1Jet_pt"]
    
    # Jet columns
    Jet_cols = ["Jet_eta", "Jet_phi", "Jet_pt", "Jet_mass", "Jet_jetId", "Jet_nConstituents", "Jet_rawFactor", "Jet_area"]
    
    # HLT columns
    HLT_cols = ["HLT_PFJet500"]
    
    # Event information
    Event_cols = ["run", "luminosityBlock", "event", "bunchCrossing", "Rho_fixedGridRhoFastjetAll"]
    
    selected_columns = L1_cols + Jet_cols + HLT_cols + Event_cols
    
    # Create RDataFrame
    rdf = RDataFrame(chain)
    print("RDF created")
    
    # Filter jets
    print("Filtering events")
    rdf = (rdf.Filter("HLT_PFJet500", "Filter events with HLT_PFJet500")
           .Filter("Jet_pt.size() > 0", "Filter events with at least one jet")
        )
    
    # Recalculate the jet pt
    rdf = (rdf.Define("OldJet_pt", "Jet_pt")
        .Define("Jet_rawPt", "Jet_pt*(1.0 - Jet_rawFactor)")
        .Define("C", "CorrectedJetPt(rdfslot_, rdfentry_, Jet_rawPt, Jet_eta, Jet_area, Rho_fixedGridRhoFastjetAll)")
        .Redefine("Jet_pt", "C * Jet_rawPt")
        .Redefine("Jet_rawFactor", "1-1/C")
        )

    # Print the number of events
    # Triggers the evaluation of the previous filters
    print("Number of events:")
    print(rdf.Count().GetValue())
    
    writed_columns = [col for col in selected_columns if col not in ["Jet_rawFactor", "Jet_area", "Rho_fixedGridRhoFastJetArea", ]] + ["C"]
    
    # Write the dataframe to a ROOT file
    print(f"Writing dataframe to file {outputFile}.root")
    rdf.Snapshot("Events", outputFile+".root", selected_columns + ["C"])# , selected_columns , selected_columns + ["C"]
    