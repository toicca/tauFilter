import ROOT


# RDF
rdf = ROOT.RDataFrame("Events", "tauers.root")

# Plot the column C
canv = ROOT.TCanvas("canv", "canv", 800, 600)
h = rdf.Histo1D("Jet_pt")
h2 = rdf.Histo1D("OldJet_pt")
h.Draw()
h2.Draw("same")
canv.Draw()
canv.SaveAs("test0.png")