import ROOT

rdf = ROOT.RDataFrame("Events", "/media/DATA/NANO_DATA/2023/JetMET0_Run2023C-PromptNanoAODv11p9_v1-v1_NANOAOD/a5a36540-67cd-4853-920a-e55c3c1bcb47.root")

# Filter events with HLT_PFJet550
rdf = rdf.Filter("HLT_PFJet550 == 1", "HLT_PFJet550")

# Plot the events with HLT_PFJet500
canv = ROOT.TCanvas("canv", "canv", 800, 600)
h = rdf.Histo1D("HLT_PFJet500")
h.Draw()
canv.Draw()
canv.SaveAs("prescale_test.png")