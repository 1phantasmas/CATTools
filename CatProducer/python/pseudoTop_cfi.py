import FWCore.ParameterSet.Config as cms

partonTop = cms.EDProducer("PartonTopProducer",
    genParticles = cms.InputTag("prunedGenParticles"),
)

pseudoTop = cms.EDProducer("PseudoTopProducer",
    genParticles = cms.InputTag("prunedGenParticles"),
    finalStates = cms.InputTag("packedGenParticles"),
    leptonMinPt = cms.double(20),
    leptonMaxEta = cms.double(2.4),
    jetMinPt = cms.double(20),
    jetMaxEta = cms.double(2.4),
    leptonConeSize = cms.double(0.1),
    jetConeSize = cms.double(0.5),
    wMass = cms.double(80.2),
    tMass = cms.double(172.5),
)
