import ROOT,copy

def hist_maker(name, title, bin_set, x_name, y_name, tr, br, cut):
    hist = ROOT.TH1F(name, title, bin_set[0], bin_set[1], bin_set[2])
    #hist.GetXaxis().SetTitle(x_name)
    #hist.GetYaxis().SetTitle(y_name)
    #hist.SetLineColor(color)
    #hist.Sumw2()
    #hist.SetStats(0)
    tr.Project(name, br, cut)
    return hist

datalumi = 49.502
plotvar = "ll_m"
tcut = "step == 2 && isTight"
bin_set = [250, 0, 250]
x_name = "a.u."
y_name = "M [GeV]"

mcfilelist = {'DYJetsToLL_M-50':6025.2 ,
              'TTJets_TuneCUETP8M1_13TeV-madgraphMLM':831.8,
              'ZZ_TuneCUETP8M1_13TeV':31.8,
              'WW_TuneCUETP8M1_13TeV':65.9,
              'WZ_TuneCUETP8M1_13TeV':118.7}

rdfilelist = [#'DoubleMuon',
               'SingleMuon']

hs = ROOT.THStack(plotvar,plotvar)
h_rd = ROOT.TH1F(plotvar, plotvar, bin_set[0], bin_set[1], bin_set[2])
h_rd.SetMarkerStyle(20)
leg = ROOT.TLegend(0.7,0.7,0.9,0.9)
leg.AddEntry(h_rd,"Data","p")

j=1
for i in mcfilelist:
    j=j+1
    rootfilename = i+".root"
    print rootfilename
    samplename = i.strip().split("_")[0]
    tt = ROOT.TFile(rootfilename)
    tree = tt.h2mu.Get("tree")
    # untill better way to get nentries
    tempdraw = plotvar +" >> temp" +samplename
    tree.Draw(tempdraw)
    temphist = ROOT.gDirectory.Get("temp" +samplename)
    scale = mcfilelist[i]*datalumi / temphist.GetEntries()
    print mcfilelist[i]
    histo = copy.deepcopy(hist_maker(samplename, plotvar, bin_set, x_name, y_name, tree, plotvar, tcut))
    histo.SetFillColor(j)
    histo.Scale(scale)
    hs.Add(histo)
    leg.AddEntry(histo,samplename,"f")

for i in rdfilelist:
    rootfilename = i+".root"
    print rootfilename
    samplename = i.strip().split("_")[0]
    tt = ROOT.TFile(rootfilename)
    tree = tt.h2mu.Get("tree")
    histo = copy.deepcopy(hist_maker(samplename, plotvar, bin_set, x_name, y_name, tree, plotvar, tcut))
    h_rd.Add(histo)
    
canvas = ROOT.TCanvas(plotvar,plotvar)
hs.Draw()
h_rd.Draw("psame")
leg.Draw("same")
canvas.SaveAs(plotvar+".root")
canvas.SaveAs(plotvar+".eps")

#dilepmass = ROOT.gDirectory.Get("dilepmass")

