import FWCore.ParameterSet.Config as cms

catElectrons = cms.EDProducer("CATElectronProducer",
    # input collection
    src = cms.InputTag("selectedPatElectronsPFlow"),
    vertexLabel = cms.InputTag("offlinePrimaryVertices"),
    rhoLabel = cms.InputTag("kt6PFJets", "rho"),
    runOnMC = cms.bool(True)
)

