import FWCore.ParameterSet.Config as cms
import RecoMET.METProducers.METSigParams_cfi as jetResolutions
from CondCore.DBCommon.CondDBSetup_cfi import *
    
def catSetup(process, runOnMC=True, doSecVertex=True):    
    process.load("CATTools.CatProducer.eventCleaning.eventCleaning_cff")
    process.load("CATTools.CatProducer.catCandidates_cff")
    process.p += process.eventCleaning

    catJetsSource = "selectedPatJetsPFlow"
    catGenJetsSource = "ak5GenJets"
    catMuonsSource = "selectedPatMuonsPFlow"
    catElectronsSource = "selectedPatElectronsPFlow"
    catPhotonsSource = "selectedPatPhotons"
    catTausSource = "selectedPatTausPFlow"
    catMETsSource = "patMETsPFlow"
    catVertexSource = "offlinePrimaryVertices"
    catMCsource = "genParticles"
    catBeamSpot = "offlineBeamSpot"
    #catRho = "kt6PFJets"
    
    process.catJets.src = cms.InputTag(catJetsSource)
    process.catMuons.src = cms.InputTag(catMuonsSource)
    process.catMuons.mcLabel = cms.InputTag(catMCsource)
    process.catMuons.vertexLabel = cms.InputTag(catVertexSource)
    process.catMuons.beamLineSrc = cms.InputTag(catBeamSpot)
    process.catElectrons.src = cms.InputTag(catElectronsSource)
    process.catElectrons.vertexLabel = cms.InputTag(catVertexSource)
    process.catElectrons.mcLabel = cms.InputTag(catMCsource)
    process.catElectrons.beamLineSrc = cms.InputTag(catBeamSpot)
    #process.catElectrons.rhoLabel = cms.InputTag(catRho)
    process.catPhotons.src = cms.InputTag(catPhotonsSource)
    process.catTaus.src = cms.InputTag(catTausSource)
    process.catMETs.src = cms.InputTag(catMETsSource)
    process.catGenJets.src = cms.InputTag(catGenJetsSource)
    process.catSecVertexs.muonSrc = cms.InputTag(catMuonsSource)
    process.catSecVertexs.elecSrc = cms.InputTag(catElectronsSource)
    process.catSecVertexs.vertexLabel = cms.InputTag(catVertexSource)

    process.load("CondCore.DBCommon.CondDBCommon_cfi")
    process.jec = cms.ESSource("PoolDBESSource",
      DBParameters = cms.PSet(
        messageLevel = cms.untracked.int32(0)
        ),
      timetype = cms.string('runnumber'),
      toGet = cms.VPSet(
      cms.PSet(
            record = cms.string('JetCorrectionsRecord'),
            tag    = cms.string('JetCorrectorParametersCollection_Winter14_V5_DATA_AK5PF'),
            ),
      ), 
      connect = cms.string('sqlite:Winter14_V5_DATA.db')
    )
    process.es_prefer_jec = cms.ESPrefer('PoolDBESSource','jec')

    process.load("CATTools.CatProducer.recoEventInfo_cfi")
    process.recoEventInfo.vertex = cms.InputTag(catVertexSource)
    process.out.outputCommands.append("keep *_recoEventInfo_*_*")
    process.p += process.recoEventInfo 
    if runOnMC:
        ## Load MC dependent producers
        process.load("CATTools.CatProducer.pdfWeight_cff")
        process.load("CATTools.CatProducer.pileupWeight_cff")
        process.out.outputCommands.append("keep *_pdfWeight_*_*")
        process.out.outputCommands.append("keep *_pileupWeight_*_*")
        process.p += process.pdfWeight +  process.pileupWeight
        ## making met Uncertainty
        ## from PhysicsTools.PatUtils.tools.metUncertaintyTools import runMEtUncertainties
        ## runMEtUncertaintiesClass = runMEtUncertainties(process,
        ##                     electronCollection = cms.InputTag(catElectronsSource),
        ##                     jetCollection = cms.InputTag(catJetsSource),
        ##                     muonCollection = cms.InputTag(catMuonsSource),
        ##                     tauCollection = cms.InputTag(catTausSource),
        ## )
        ## process.patDefaultSequencePFlow += process.metUncertaintySequence

        ## added smeared and shifted jets
        jetSmearFileName = 'PhysicsTools/PatUtils/data/pfJetResolutionMCtoDataCorrLUT.root'
        jetSmearHistogram = 'pfJetResolutionMCtoDataCorrLUT'
        varyByNsigmas = 1.0
        
        process.smearedJetsRes = cms.EDProducer("SmearedPATJetProducer",
            src = cms.InputTag(catJetsSource),
            dRmaxGenJetMatch = cms.string('TMath::Min(0.5, 0.1 + 0.3*TMath::Exp(-0.05*(genJetPt - 10.)))'),
            sigmaMaxGenJetMatch = cms.double(5.),                               
            inputFileName = cms.FileInPath(jetSmearFileName),
            lutName = cms.string(jetSmearHistogram),
            jetResolutions = jetResolutions.METSignificance_params,
            skipJetSelection = cms.string('jecSetsAvailable & abs(energy - correctedP4("Uncorrected").energy) > (5.*min(energy, correctedP4("Uncorrected").energy))'),
            skipRawJetPtThreshold = cms.double(10.), # GeV
            skipCorrJetPtThreshold = cms.double(1.e-2),
            )
        process.smearedJetsResDown = process.smearedJetsRes.clone(
            shiftBy = cms.double(-1.*varyByNsigmas)
        )
        process.smearedJetsResUp = process.smearedJetsRes.clone(
            shiftBy = cms.double(+1.*varyByNsigmas)
        )
        process.p += process.smearedJetsRes + process.smearedJetsResDown + process.smearedJetsResUp
      
        process.shiftedJetsEnUp = cms.EDProducer("ShiftedPATJetProducer",
            src = cms.InputTag(catJetsSource),
            #jetCorrPayloadName = cms.string(jetCorrPayloadName),
            #jetCorrUncertaintyTag = cms.string('Uncertainty'),
            jetCorrInputFileName = cms.FileInPath('PhysicsTools/PatUtils/data/Summer12_V2_DATA_AK5PF_UncertaintySources.txt'),
            jetCorrUncertaintyTag = cms.string("SubTotalDataMC"),
            addResidualJES = cms.bool(True),
            jetCorrLabelUpToL3 = cms.string("ak5PFL1FastL2L3"),
            jetCorrLabelUpToL3Res = cms.string("ak5PFL1FastL2L3Residual"),                               
            shiftBy = cms.double(+1.*varyByNsigmas)
        )
        process.shiftedJetsEnDown = process.shiftedJetsEnUp.clone(
            shiftBy = cms.double(-1.*varyByNsigmas)
        )
        process.p += process.shiftedJetsEnUp + process.shiftedJetsEnDown

        process.catJets.shiftedEnDownSrc = cms.InputTag("shiftedJetsEnDown")
        process.catJets.shiftedEnUpSrc = cms.InputTag("shiftedJetsEnUp")
        process.catJets.smearedResSrc = cms.InputTag("smearedJetsRes")
        process.catJets.smearedResDownSrc = cms.InputTag("smearedJetsResDown")
        process.catJets.smearedResUpSrc = cms.InputTag("smearedJetsResUp")

    if not runOnMC:
        process.makeCatCandidates.remove(process.catGenJets)
        process.makeCatCandidates.remove(process.catMCParticles)
        process.catMuons.runOnMC = cms.bool(False)
        process.catElectrons.runOnMC = cms.bool(False)
        process.catJets.runOnMC = cms.bool(False)

    if doSecVertex:
        from TrackingTools.TransientTrack.TransientTrackBuilder_cfi import TransientTrackBuilderESProducer
        setattr(process, "TransientTrackBuilderESProducer", TransientTrackBuilderESProducer)
        process.makeCatCandidates += process.catSecVertexs
        
    ## cuts on selected Pat objects
    getattr(process,catJetsSource).cut = cms.string("pt > 20")
    process.pfSelectedMuonsPFlow.cut = cms.string("")

    #getattr(process,catMuonsSource).cut = cms.string("pt > 5 || isPFMuon || (pt > 3 && (isGlobalMuon || isStandAloneMuon || numberOfMatches > 0 || muonID('RPCMuLoose')))") 
    #getattr(process,catElectronsSource).cut = cms.string("pt > 5") 
    #getattr(process,catPhotonsSource).cut = cms.string("pt > 5")

    process.p += process.makeCatCandidates

    process.out.outputCommands = cms.untracked.vstring(
        'drop *',
        'keep *_cat*_*_*',
        'keep *_goodOfflinePrimaryVertices*_*_*',
        'keep GenEventInfoProduct_*_*_*',
        'keep PileupSummaryInfos_*_*_*',
        'keep edmMergeableCounter_*_*_*',
        'keep patTriggerPaths_patTrigger*_*_*',
        'keep recoGenParticles_genParticles__SIM',
        'keep recoGenJets_{0}_*_*'.format(catJetsSource),
        )
    process.options = cms.untracked.PSet(wantSummary = cms.untracked.bool(False))
