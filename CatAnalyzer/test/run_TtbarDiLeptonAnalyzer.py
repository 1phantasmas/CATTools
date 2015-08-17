import FWCore.ParameterSet.Config as cms

process = cms.Process("TtbarDiLeptonAnalyzer")
process.options = cms.untracked.PSet( wantSummary = cms.untracked.bool(False) )
process.options.allowUnscheduled = cms.untracked.bool(True)

process.load("FWCore.MessageService.MessageLogger_cfi")
process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

###### discard this line when use for data sample ##########
process.partonTop = cms.EDProducer("PartonTopProducer",
    genParticles = cms.InputTag("prunedGenParticles"),
    jetMinPt = cms.double(20),
    jetMaxEta = cms.double(2.5),
    jetConeSize = cms.double(0.4),
)
###### discard this line when use for data sample ##########

process.source = cms.Source("PoolSource", fileNames = cms.untracked.vstring())

"""
for i in xrange(1,101):
#    process.source.fileNames.append('file:/cms/data/xrd/store/user/jlee/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/cat74v2_RunIISpring15DR74-Asympt50ns_MCRUN2_74_V9A-v1/150713_164609/0000/catTuple_%d.root' % i)
	process.source.fileNames.append('file:/cms/scratch/CAT/TTJets_TuneCUETP8M1_13TeV-madgraphMLM-pythia8/v7-3-0_RunIISpring15DR74-Asympt50ns_MCRUN2_74_V9A-v1/150720_065809/0000/catTuple_%d.root'%i)
"""
#process.source.fileNames.append('file:/cms/scratch/CAT/MuonEG/v7-3-0_Run2015B-PromptReco-v1/150720_060935/0000/catTuple_1.root')
process.source.fileNames.append('/store/group/CAT/TT_TuneCUETP8M1_13TeV-powheg-pythia8/v7-3-4_RunIISpring15DR74-Asympt50ns_MCRUN2_74_V9A-v4/150810_215031/0000/catTuple_101.root')
#process.source.fileNames.append('file:/afs/cern.ch/user/j/jlee/test/cat74/src/CATTools/CatProducer/prod/catTuple.root')

process.ttll = cms.EDAnalyzer("TtbarDiLeptonAnalyzer",
    vertices = cms.InputTag("catVertex"),
    #vertices = cms.InputTag("offlineSlimmedPrimaryVertices"),
    muons = cms.InputTag("catMuons"),
    electrons = cms.InputTag("catElectrons"),
    jets = cms.InputTag("catJets"),
    mets = cms.InputTag("catMETs"),
    mcLabel = cms.InputTag("prunedGenParticles"),
    
    partonTop_channel = cms.InputTag("partonTop","channel"),
    partonTop_modes = cms.InputTag("partonTop", "modes"),
    partonTop_genParticles = cms.InputTag("partonTop"),

    pseudoTop_jets = cms.InputTag("pseudoTop","jets"),
    pseudoTop_leptons = cms.InputTag("pseudoTop","leptons"),
    pseudoTop = cms.InputTag("pseudoTop"),
    pseudoTop_neutrinos = cms.InputTag("pseudoTop","neutrinos"),
    pseudoTop_mets = cms.InputTag("pseudoTop","mets"),
    
    tmassbegin = cms.double(100),
    tmassend   = cms.double(300),
    tmassstep  = cms.double(  1),
    neutrino_parameters = cms.vdouble(27.23,53.88,19.92,53.89,19.9)
)

process.TFileService = cms.Service("TFileService",
    fileName = cms.string("top.root"
))

process.p = cms.Path(process.ttll)
process.MessageLogger.cerr.FwkReport.reportEvery = 50000
