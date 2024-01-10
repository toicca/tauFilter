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
isMC = False

# Dictionary of IOV to JEC object
JEC_dict = {"2022B" : "Summer22-22Sep2023_Run2022CD_V3_DATA",
            "2022C" : "Summer22-22Sep2023_Run2022CD_V3_DATA",
            "2022D" : "Summer22-22Sep2023_Run2022CD_V3_DATA",
            "2022E" : "Summer22EE-22Sep2023_Run2022E_V3_DATA",
            "2022F" : "Summer22EEPrompt22_Run2022F_V3_DATA",
            "2022G" : "Summer22EEPrompt22_Run2022G_V3_DATA",
            "2023B" : "Summer22Prompt23_Run2023Cv123_V3_DATA",
            "2023Cv123" : "Summer22Prompt23_Run2023Cv123_V3_DATA",
            "2023Cv4" : "Summer22Prompt23_Run2023Cv4_V3_DATA",
            "2023D" : "Summer22Prompt23_Run2023D_V3_DATA"}

def getOptions():
    parser = argparse.ArgumentParser(description="Run a tau filter on Run 3 data")
    parser.add_argument("-f_in", "--inputFiles", type=str, default=inputFiles, nargs='+', help="Input files")
    parser.add_argument("-o", "--outputFile", type=str, default=outputFile, help="Output file name")
    parser.add_argument("-IOV", "--IOV", type=str, default="2023Cv123", help="IOV of the JEC to use")
    parser.add_argument("-isMC", "--isMC", type=bool, default=isMC, help="Is the input file MC?")
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
    isMC = args.isMC
    
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
                            const char* L2L3ResidualFile = Form("../JetMETObjects/data/""" + CorrectionSet + """_L2L3Residual_AK4PFPuppi.txt");
                            
                            JetCorrectorParameters *L2Relative = new JetCorrectorParameters(L2RelativeFile);
                            JetCorrectorParameters *L2L3Residual = new JetCorrectorParameters(L2L3ResidualFile);
                            
                            correctionParameters.push_back(*L2Relative);
                            correctionParameters.push_back(*L2L3Residual);
                        }
                        
                        /*
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
                        */
std::vector<Float_t> CorrectedJetPt(unsigned int slot, ULong64_t entry,const ROOT::RVec<Float_t>& JetPt, const ROOT::RVec<Float_t>& JetEta, const ROOT::RVec<Float_t>& JetArea, Float_t Rho) {
    std::unique_ptr<FactorizedJetCorrector> JetCorrector;
    std::vector<Float_t> CorrectedJetPt(JetPt.size());

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

Float_t* MultiplyRVecAndFloatPointer(const ROOT::RVec<Float_t>& rvec, const Float_t* floatArray, size_t size) {
    Float_t* result = new Float_t[size];

    for (size_t i = 0; i < size; ++i) {
        result[i] = rvec[i] * floatArray[i];
    }

    return result;
}

std::vector<Float_t> MultiplyStdVectorAndRVec(const std::vector<Float_t>& stdVector, const ROOT::RVec<Float_t>& rvec) {
    // Ensure that the sizes match
    if (stdVector.size() != rvec.size()) {
        std::cerr << "Error: Sizes of the input vectors do not match." << std::endl;
        return std::vector<Float_t>();
    }

    std::vector<Float_t> result(stdVector.size());

    for (size_t i = 0; i < stdVector.size(); ++i) {
        result[i] = stdVector[i] * rvec[i];
    }

    return result;
}

std::vector<Float_t> CalculateRawFactor(const std::vector<Float_t>& C) {
    std::vector<Float_t> result;
    result.reserve(C.size()); // Reserve memory for efficiency

    for (const auto& element : C) {
        if (element != 0) {
            result.push_back(1.0 - 1.0 / element);
        } else {
            // Handle division by zero or other special cases
            result.push_back(0.0);
        }
    }

    return result;
}

std::vector<Float_t> RVectoStdVector(const ROOT::RVec<Float_t>& rvec) {
    std::vector<Float_t> result;
    result.reserve(rvec.size()); // Reserve memory for efficiency

    for (const auto& element : rvec) {
        result.push_back(element);
    }
    
    return result;
}
                        #endif
                        """)
    
    ROOT.initJEC()

    print(f"Loading {len(inputFiles)} files")
    chain = ROOT.TChain("Events")
    for file in inputFiles:
        chain.Add(file)
        
    # L1 columns
    # if not isMC:
    #     L1_cols = ["L1Tau_hwIso", "L1Tau_bx", "L1Tau_eta", "L1Tau_phi", "L1Tau_pt",
    #             "L1Jet_bx", "L1Jet_eta", "L1Jet_phi", "L1Jet_pt",
    #             "L1_UnprefireableEvent",
    #             "L1EtSum_bx", "L1EtSum_etSumType", "L1EtSum_phi", "L1EtSum_pt"]
    # else:
    #     L1_cols = []
    
    L1_cols = []
    
    # Jet columns
    Jet_cols = ["Jet_eta", "Jet_phi", "Jet_pt", "Jet_mass", "Jet_jetId", "Jet_nConstituents", "Jet_rawFactor", "Jet_area"]
    
    # HLT columns
    HLT_cols = ["HLT_PFJet500"]
    
    # Flag columns
    Flag_cols = ['Flag_goodVertices', 'Flag_globalSuperTightHalo2016Filter', 
                 'Flag_HBHENoiseFilter', 'Flag_HBHENoiseIsoFilter', 
                 'Flag_EcalDeadCellTriggerPrimitiveFilter', 'Flag_BadPFMuonFilter', 
                 'Flag_BadPFMuonDzFilter', 'Flag_globalTightHalo2016Filter', 'Flag_CSCTightHaloFilter', 
                 'Flag_ecalBadCalibFilter', 'Flag_eeBadScFilter']

    # Event information
    Event_cols = ["run", "luminosityBlock", "event", "bunchCrossing", "Rho_fixedGridRhoFastjetAll"]
    
    selected_columns = L1_cols + Jet_cols + HLT_cols + Event_cols

    flag_filt = """
        (Flag_goodVertices) &&
        (Flag_globalSuperTightHalo2016Filter) &&
        (Flag_HBHENoiseFilter) &&
        (Flag_HBHENoiseIsoFilter) &&
        (Flag_EcalDeadCellTriggerPrimitiveFilter) &&
        (Flag_BadPFMuonFilter) &&
        (Flag_BadPFMuonDzFilter) &&
        (Flag_globalTightHalo2016Filter) &&
        (Flag_CSCTightHaloFilter) &&
        (Flag_ecalBadCalibFilter) && 
        (Flag_eeBadScFilter)
        """.replace("\n", "").replace("\t", "")
    
    # Create RDataFrame
    rdf = RDataFrame(chain)
    print("RDF created")
    
    # Filter jets
    print("Filtering events")
    rdf = (rdf.Filter("Jet_pt.size() > 0", "Filter events with at least one jet")
           .Define("Flag_Run3", flag_filt)
        )
    
    # Take the three leading jets
    for col in Jet_cols:
        rdf = rdf.Redefine(col, strTakeN(col, 3))
    
    if not isMC:
        rdf = rdf.Filter("HLT_PFJet500", "Filter events with HLT_PFJet500")
    else:
        rdf = rdf.Filter("Jet_pt[0] > 600", "Filter events with leading jet pt > 600 GeV")
    
    # Recalculate the jet pt
    if not isMC:
        rdf = (rdf.Define("OldJet_pt", "Jet_pt")
            .Define("Jet_rawPt", "Jet_pt*(1.0 - Jet_rawFactor)")
            .Define("C", "CorrectedJetPt(rdfslot_, rdfentry_, Jet_rawPt, Jet_eta, Jet_area, Rho_fixedGridRhoFastjetAll)")
            .Redefine("Jet_pt", "MultiplyStdVectorAndRVec(C, Jet_rawPt)")
            .Redefine("Jet_rawFactor", "CalculateRawFactor(C)")
            )
        

        
    for col in Jet_cols:
        rdf = rdf.Redefine(col, f"RVectoStdVector({col})")
        
    # Redefine nJet with the size
    # rdf = rdf.Redefine("nJet", "Jet_pt.size()")

    # Print the number of events
    # Triggers the evaluation of the previous filters
    print("Number of events:")
    print(rdf.Count().GetValue())
    
    writed_columns = [col for col in selected_columns if col not in ["Jet_area", "Rho_fixedGridRhoFastjetAll"]]
    
    # Check that all the columns to write are in the dataframe
    rdf_cols = rdf.GetColumnNames()
    for col in writed_columns:
        if col not in rdf_cols:
            print(f"Column {col} not in dataframe")
            # Remove the column from the list of columns to write
            writed_columns.remove(col)

    if isMC:
        writed_columns += ["genWeight"]
    
    # Write the dataframe to a ROOT file
    print(f"Writing dataframe to file {outputFile}.root")
    rdf.Snapshot("Events", outputFile+".root", writed_columns + ["Flag_Run3"])
    print("Done writing to file")
    