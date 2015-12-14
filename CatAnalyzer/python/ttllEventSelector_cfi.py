import FWCore.ParameterSet.Config as cms
from CATTools.CatAnalyzer.leptonSF_cff import *

ttll = cms.EDFilter("TTLLEventSelector",
    isMC = cms.bool(True),
    filterCutStepBefore = cms.int32(4),

    # Physics objects
    muon = cms.PSet(
        src = cms.InputTag("catMuons"),
        scaleDirection = cms.int32(0),
        #scaleDirection = cms.int32(-1),
        #scaleDirection = cms.int32(+1),
        efficiencySF = muonSFTight,
    ),

    electron = cms.PSet(
        src = cms.InputTag("catElectrons"),
        idName = cms.string("cutBasedElectronID-Spring15-25ns-V1-standalone-medium"),
        scaleDirection = cms.int32(0),
        #scaleDirection = cms.int32(-1),
        #scaleDirection = cms.int32(+1),
        efficiencySF = electronSFCutBasedMedium,
    ),

    jet = cms.PSet(
        src = cms.InputTag("catJets"),
        bTagName = cms.string("pfCombinedInclusiveSecondaryVertexV2BJetTags"),
        bTagWP = cms.string("CSVM"),
        scaleDirection = cms.int32(0),
        #scaleDirection = cms.int32(-1),
        #scaleDirection = cms.int32(+1),
        resolDirection = cms.int32(0),
        #resolDirection = cms.int32(-1),
        #resolDirection = cms.int32(+1),
    ),

    met = cms.PSet(
        src = cms.InputTag("catMETs"),
    ),

    vertex = cms.PSet(
        nVertex = cms.InputTag("catVertex", "nGoodPV"),
        #src = cms.InputTag("catVertex"),
        pileupWeight = cms.InputTag("pileupWeight"),
    ),

    # Filters
    filters = cms.PSet(
        filterRECO = cms.InputTag("filterRECO"),
        trigMUEL = cms.InputTag("filterTrigMUEL"),
        trigMUMU = cms.InputTag("filterTrigMUMU"),
        trigELEL = cms.InputTag("filterTrigELEL"),
    ),

    # Event weights
    genWeight = cms.PSet(
        index = cms.uint32(0),
        src = cms.InputTag("genWeight", "genWeight"),
    ),
)

