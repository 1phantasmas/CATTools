import FWCore.ParameterSet.Config as cms

catMuons = cms.EDProducer("CATMuonProducer",
    src = cms.InputTag("patMuons"),
    mcLabel = cms.InputTag("genParticles"),
    vertexLabel = cms.InputTag("offlinePrimaryVertices"),
    beamLineSrc = cms.InputTag("offlineBeamSpot"),
    runOnMC = cms.bool(True)
)

catElectrons = cms.EDProducer("CATElectronProducer",
    src = cms.InputTag("patElectrons"),
    mcLabel = cms.InputTag("genParticles"),
    vertexLabel = cms.InputTag('offlinePrimaryVertices'),
    beamLineSrc = cms.InputTag("offlineBeamSpot"),
    rhoLabel = cms.InputTag("fixedGridRhoAll", "rho"),
    runOnMC = cms.bool(True)
)

catPhotons = cms.EDProducer("CATPhotonProducer",
    src = cms.InputTag("selectedPatPhotons"),
)

catJets = cms.EDProducer("CATJetProducer",
    src = cms.InputTag("selectedPatJetsPFlow"),
)

catMETs = cms.EDProducer("CATMETProducer",
    src = cms.InputTag("patMETsPFlow"),
)

catGenJets = cms.EDProducer("CATGenJetProducer",
    src = cms.InputTag("ak5GenJets"),
    pt = cms.double(10),
    eta = cms.double(2.5)
)

catMCParticles = cms.EDProducer("CATMCParticleProducer",
    src = cms.InputTag("genParticles"),
    pt = cms.double(10),
    eta = cms.double(2.5)
)

catGenTops = cms.EDProducer("CATGenTopProducer",
    genJetLabel = cms.InputTag("ak5GenJets"),
    mcParticleLabel = cms.InputTag("genParticles"),
)

catSecVertexs = cms.EDProducer("CATSecVertexProducer",
    muonSrc = cms.InputTag("selectedPatMuonsPFlow"),
    elecSrc = cms.InputTag("selectedPatElectronsPFlow"),
    vertexLabel = cms.InputTag("goodOfflinePrimaryVertices"),
    track = cms.PSet(
        minPt = cms.double(1.0),
        maxEta = cms.double(2.5),
        chi2 = cms.double(5.),
        nHit = cms.int32(6),
        signif = cms.double(-5),
        DCA = cms.double(1.),
    ),
    vertex = cms.PSet(
        chi2 = cms.double(7.),
        minLxy = cms.double(-100),
        maxLxy = cms.double(100),
        signif = cms.double(-5.0),
    ),
    rawMassMin = cms.double(2),
    rawMassMax = cms.double(4),
    massMin = cms.double(2.80),
    massMax = cms.double(3.40),
)

makeCatCandidates =  cms.Sequence( 
    catMuons*
    catElectrons*
    catPhotons*
    catJets*
    catMETs*
    # MC information below
    catGenJets*
    # dont need for now
    #catGenTops*
    catMCParticles*
    catSecVertexs
) 
