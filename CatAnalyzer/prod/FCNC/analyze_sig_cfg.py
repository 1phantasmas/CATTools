import FWCore.ParameterSet.Config as cms
process = cms.Process("CATeX")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(True) )

process.options.allowUnscheduled = cms.untracked.bool(True)
process.MessageLogger.cerr.FwkReport.reportEvery = 50000

process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())
from CATTools.Validation.commonTestInput_cff import commonTestCATTuples
process.source.fileNames = commonTestCATTuples["sig"]
process.load("CATTools.CatAnalyzer.filters_cff")
process.load("CATTools.Validation.topFCNCEventSelector_cff")
process.load("CATTools.CatAnalyzer.ttll.ttllGenFilters_cff")
process.load("CATTools.Validation.validation_cff")

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("ntuple.root"),
)

process.load("CATTools.CatAnalyzer.flatGenWeights_cfi")
process.load("CATTools.CatProducer.mcTruthTop.partonTop_cfi")
process.agen = cms.EDAnalyzer("CATGenTopAnalysis",
    weightIndex = cms.int32(-1),
    weight = cms.InputTag("flatGenWeights"),
    channel = cms.InputTag("partonTop","channel"),
    modes = cms.InputTag("partonTop", "modes"),
    partonTop = cms.InputTag("partonTop"),
    pseudoTop = cms.InputTag("pseudoTop"),
    filterTaus = cms.bool(False),
)

process.load("CATTools.CatProducer.pileupWeight_cff")
from CATTools.CatProducer.pileupWeight_cff import pileupWeightMap
process.pileupWeight.weightingMethod = "RedoWeight"
process.pileupWeight.pileupMC = pileupWeightMap["2016_25ns_SpringMC"]
process.pileupWeight.pileupRD = pileupWeightMap["Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON"]
process.pileupWeight.pileupUp = pileupWeightMap["Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON_Up"]
process.pileupWeight.pileupDn = pileupWeightMap["Cert_271036-284044_13TeV_23Sep2016ReReco_Collisions16_JSON_Dn"]
process.eventsFCNC.vertex.pileupWeight = "pileupWeight::CATeX"

process.eventsFCNC.filters.filterRECO = "filterRECOMC"
process.eventsFCNC.filters.ignoreTrig = True

process.el = process.eventsFCNC.clone(channel = cms.string("electron"))
process.mu = process.eventsFCNC.clone(channel = cms.string("muon"))
delattr(process, 'eventsFCNC')

process.load("CATTools.CatAnalyzer.csvWeights_cfi")
process.csvWeightsEL = process.csvWeights.clone(src = cms.InputTag("el:jets"))
process.csvWeightsMU = process.csvWeights.clone(src = cms.InputTag("mu:jets"))
delattr(process, "csvWeights")

process.load("CATTools.CatAnalyzer.analyzers.topFCNCNtuple_cff")
process.ntupleFCNC.puWeight = process.el.vertex.pileupWeight
process.ntupleEL = process.ntupleFCNC.clone(
    src = cms.InputTag("el"),
    csvWeight = cms.InputTag("csvWeightsEL"),
    csvWeightSyst = cms.InputTag("csvWeightsEL:syst"),
)
process.ntupleMU = process.ntupleFCNC.clone(
    src = cms.InputTag("mu"),
    csvWeight = cms.InputTag("csvWeightsMU"),
    csvWeightSyst = cms.InputTag("csvWeightsMU:syst"),
)
delattr(process, 'ntupleFCNC')

process.p_el = cms.Path(
    process.agen + process.filterPartonTTLJ
  * process.gen + process.rec
  * process.el * process.ntupleEL
)

process.p_mu = cms.Path(
    process.agen + process.filterPartonTTLJ
  * process.gen + process.rec
  * process.mu * process.ntupleMU
)

## Customise with cmd arguments
import sys
if len(sys.argv) > 2:
    for l in sys.argv[2:]: exec('process.'+l)
