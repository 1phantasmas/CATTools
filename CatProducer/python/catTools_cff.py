import FWCore.ParameterSet.Config as cms
import catDefinitions_cfi as cat
import os
print os.environ['CMSSW_BASE']

from CondCore.DBCommon.CondDBSetup_cfi import *

def catTool(process, runOnMC=True, useMiniAOD=True):
    if runOnMC:
        from CATTools.CatProducer.pileupWeight_cff import pileupWeightMap
        process.pileupWeight.pileupMC = pileupWeightMap[cat.pileupMCmap]
        process.pileupWeight.pileupRD = pileupWeightMap["%s"%cat.lumiJSON]
        process.pileupWeight.pileupUp = pileupWeightMap["%s_Up"%cat.lumiJSON]
        process.pileupWeight.pileupDn = pileupWeightMap["%s_Dn"%cat.lumiJSON]
    else:
        from FWCore.PythonUtilities.LumiList import LumiList
        process.lumiMask = cms.EDFilter("LumiMaskFilter",
            LumiSections = LumiList('%s/src/CATTools/CatProducer/data/LumiMask/%s.txt'%(os.environ['CMSSW_BASE'], cat.lumiJSON)).getVLuminosityBlockRange())
    
    useJECfile = True
    jecFile = cat.JetEnergyCorrection
    if runOnMC:
        jecFile = jecFile+"_MC"
    else:
        jecFile = jecFile+"_DATA"
    if useJECfile:
        from CondCore.CondDB.CondDB_cfi import CondDB
        CondDB.__delattr__('connect')
        process.jec = cms.ESSource("PoolDBESSource",CondDB,
            connect = cms.string('sqlite_fip:CATTools/CatProducer/data/JEC/%s.db'%jecFile),            
            toGet = cms.VPSet(
                cms.PSet(
                    record = cms.string("JetCorrectionsRecord"),
                    tag = cms.string("JetCorrectorParametersCollection_%s_AK4PF"%jecFile),
                    label= cms.untracked.string("AK4PF")),
                cms.PSet(
                    record = cms.string("JetCorrectionsRecord"),
                    tag = cms.string("JetCorrectorParametersCollection_%s_AK4PFchs"%jecFile),
                    label= cms.untracked.string("AK4PFchs")),
                cms.PSet(
                    record = cms.string("JetCorrectionsRecord"),
                    tag = cms.string("JetCorrectorParametersCollection_%s_AK4PFPuppi"%jecFile),
                    label= cms.untracked.string("AK4PFPuppi")),
            )
        )
        process.es_prefer_jec = cms.ESPrefer("PoolDBESSource","jec")
        print "JEC based on", process.jec.connect
    
    if useMiniAOD: ## corrections when using miniAOD
        #######################################################################
        ## Event filters from MET https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2
        ## New muon filters to be run on the fly
        process.load('RecoMET.METFilters.BadPFMuonFilter_cfi')
        process.BadPFMuonFilter.muons = cms.InputTag("slimmedMuons")
        process.BadPFMuonFilter.PFCandidates = cms.InputTag("packedPFCandidates")

        process.load('RecoMET.METFilters.BadChargedCandidateFilter_cfi')
        process.BadChargedCandidateFilter.muons = cms.InputTag("slimmedMuons")
        process.BadChargedCandidateFilter.PFCandidates = cms.InputTag("packedPFCandidates")
            
        process.nEventsFiltered = cms.EDProducer("EventCountProducer")
    
        process.p += (process.BadPFMuonFilter*process.BadChargedCandidateFilter*process.nEventsFiltered)
        #######################################################################
        # adding puppi https://twiki.cern.ch/twiki/bin/view/CMS/PUPPI        
        #process.catJetsPuppi.src = cms.InputTag("slimmedJetsPuppi")
        #process.catMETsPuppi.src = cms.InputTag("slimmedMETsPuppi")
        # for puppi isolation
        ## process.packedPFCandidatesWoMuon  = cms.EDFilter("CandPtrSelector", src = cms.InputTag("packedPFCandidates"), cut = cms.string("fromPV>=2 && abs(pdgId)!=13 " ) )
        ## process.particleFlowNoMuonPUPPI.candName         = 'packedPFCandidatesWoMuon'
        ## process.particleFlowNoMuonPUPPI.vertexName       = 'offlineSlimmedPrimaryVertices'
        
        ########################################################################
        ## Setup to acess quark/gluon likelihood value

        #from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox
        #jetToolbox( process, 'ak4', 'ak4JetSubs', 'out', PUMethod='CHS', updateCollection='slimmedJets',  JETCorrPayload='AK8PFchs', miniAOD=True, addQGTagger=True )   ### For example
        #jetToolbox( process, 'ak4', 'ak4JetSubs', 'out', PUMethod='CHS', miniAOD=True, addQGTagger=True )   ### For example

#process.options.allowUnscheduled = cms.untracked.bool(True)
        qgDatabaseVersion = 'v1' # check https://twiki.cern.ch/twiki/bin/viewauth/CMS/QGDataBaseVersion
        QGPoolDBESSource = cms.ESSource("PoolDBESSource",
                CondDBSetup,
                toGet = cms.VPSet(),
                connect = cms.string('frontier://FrontierProd/CMS_COND_PAT_000')
        )

        for type in ['AK4PFchs','AK4PFchs_antib']:
            QGPoolDBESSource.toGet.extend(cms.VPSet(cms.PSet(
                record = cms.string('QGLikelihoodRcd'),
                tag    = cms.string('QGLikelihoodObject_'+qgDatabaseVersion+'_'+type),
                label  = cms.untracked.string('QGL_'+type)
           )))
        process.load('RecoJets.JetProducers.QGTagger_cfi')
        process.QGTagger.srcJets    = cms.InputTag("updatedPatJets")   # Could be reco::PFJetCollection or pat::JetCollection (both AOD and miniAOD)
        #process.QGTagger.srcJets    = cms.InputTag("slimmedJets")   # Could be reco::PFJetCollection or pat::JetCollection (both AOD and miniAOD)
        #process.QGTagger.srcJets    = cms.InputTag("selectedPatJetsAK4PFCHS")   # Could be reco::PFJetCollection or pat::JetCollection (both AOD and miniAOD)
        process.QGTagger.jetsLabel  = cms.string('QGL_AK4PFchs')        # Other options: see https://twiki.cern.ch/twiki/bin/viewauth/CMS/QGDataBaseVersion
        #######################################################################
        ## applying new jec on the fly
        process.load("PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff")
        process.patJetCorrFactors.primaryVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
        process.catJets.src = cms.InputTag("updatedPatJets")
        ### updating puppi jet jec
        process.patJetPuppiCorrFactorsUpdated = process.updatedPatJetCorrFactors.clone(
            src = process.catJetsPuppi.src,
            payload = cms.string('AK4PFPuppi'),
            levels = cms.vstring('L2Relative','L3Absolute'),
            useRho = cms.bool(False))
        
        process.patJetsPuppiUpdated = process.updatedPatJets.clone(
            jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetPuppiCorrFactorsUpdated")),
            jetSource = process.catJetsPuppi.src )
        ### updating pile Jet.
        process.load("RecoJets.JetProducers.PileupJetID_cfi")
        process.pileupJetIdUpdated = process.pileupJetId.clone(
          jets=cms.InputTag("slimmedJets"),
          inputIsCorrected=True,
          applyJec=True,
          vertexes=cms.InputTag("offlineSlimmedPrimaryVertices")
        )
        #process.patJetsUpdated.userData.userFloats.src +=['pileupJetIdUpdated:fullDiscriminant']

        process.catJetsPuppi.src = cms.InputTag("patJetsPuppiUpdated")
        process.catJetsPuppi.setGenParticle = cms.bool(False)
        ## #######################################################################
        ## Setup JER
        ## JER needs random numbers
        process.RandomNumberGeneratorService.catJets = cms.PSet(
            engineName = cms.untracked.string('TRandom3'),
            initialSeed = cms.untracked.uint32(1),
        )
        process.RandomNumberGeneratorService.catFatJets = cms.PSet(
            engineName = cms.untracked.string('TRandom3'),
            initialSeed = cms.untracked.uint32(1),
        )
        process.RandomNumberGeneratorService.catJetsPuppi = cms.PSet(
            engineName = cms.untracked.string('TRandom3'),
            initialSeed = cms.untracked.uint32(1),
        )

        ## #######################################################################
        ## # MET corrections from https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription
        #from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
        #runMetCorAndUncFromMiniAOD( process, isData= not runOnMC, jecUncFile=cat.JECUncertaintyFile, jetColl= process.catJets.src)
        #process.catMETs.src = cms.InputTag("slimmedMETs","","CAT")
        #del process.slimmedMETs.caloMET
        ## redoing noHF met due to new correction
        #process.noHFCands = cms.EDFilter("CandPtrSelector",src=cms.InputTag("packedPFCandidates"),
        #                                 cut=cms.string("abs(pdgId)!=1 && abs(pdgId)!=2 && abs(eta)<3.0"))
        #runMetCorAndUncFromMiniAOD(process,isData=not runOnMC,pfCandColl=cms.InputTag("noHFCands"),postfix="NoHF",
        #                           jecUncFile=cat.JECUncertaintyFile, jetColl= process.catJets.src)
        #process.catMETsNoHF = process.catMETs.clone(src = cms.InputTag("slimmedMETsNoHF","","CAT"))
        #del process.slimmedMETsNoHF.caloMET        
        #######################################################################
        ## Energy/Photon smearing and scale correction
        from CATTools.CatProducer.physicsObjectRecipes.egmSmearing_cff import enableElectronSmearing, enablePhotonSmearing
        enableElectronSmearing(process, runOnMC)
        enablePhotonSmearing(process, runOnMC)
        
        ## Electron/Photon VID
        from CATTools.CatProducer.physicsObjectRecipes.egmVersionedID_cff import enableElectronVID, enablePhotonVID
        enableElectronVID(process)
        enablePhotonVID(process)
       
        #######################################################################    
        # adding pfMVAMet https://twiki.cern.ch/twiki/bin/viewauth/CMS/MVAMet#Spring15_samples_with_25ns_50ns
        # https://github.com/cms-sw/cmssw/blob/CMSSW_7_4_X/RecoMET/METPUSubtraction/test/mvaMETOnMiniAOD_cfg.py
    ##     process.load("RecoJets.JetProducers.ak4PFJets_cfi")
    ##     process.ak4PFJets.src = cms.InputTag("packedPFCandidates")
    ##     process.ak4PFJets.doAreaFastjet = cms.bool(True)

    ## from JetMETCorrections.Configuration.DefaultJEC_cff import ak4PFJetsL1FastL2L3

    ## process.load("RecoMET.METPUSubtraction.mvaPFMET_cff")
    ## #process.pfMVAMEt.srcLeptons = cms.VInputTag("slimmedElectrons")
    ## process.pfMVAMEt.srcPFCandidates = cms.InputTag("packedPFCandidates")
    ## process.pfMVAMEt.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")

    ## process.puJetIdForPFMVAMEt.jec =  cms.string('AK4PF')
    ## #process.puJetIdForPFMVAMEt.jets = cms.InputTag("ak4PFJets")
    ## process.puJetIdForPFMVAMEt.vertexes = cms.InputTag("offlineSlimmedPrimaryVertices")
    ## process.puJetIdForPFMVAMEt.rho = cms.InputTag("fixedGridRhoFastjetAll")

    ## process.pfMVAMEt.inputFileNames = cms.PSet(
    ##     U     = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru_7_4_X_miniAOD_25NS_July2015.root'),
    ##     DPhi  = cms.FileInPath('RecoMET/METPUSubtraction/data/gbrphi_7_4_X_miniAOD_25NS_July2015.root'),
    ##     CovU1 = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru1cov_7_4_X_miniAOD_25NS_July2015.root'),
    ##     CovU2 = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru2cov_7_4_X_miniAOD_25NS_July2015.root')
    ## )
        
    ## process.load("PhysicsTools.PatAlgos.producersLayer1.metProducer_cfi")
    ## process.patMETsPfMva = process.patMETs.clone(addGenMET = cms.bool(False), metSource  = cms.InputTag("pfMVAMEt"))
    ## process.catMETsPfMva = process.catMETs.clone(src = cms.InputTag("patMETsPfMva"))
    ## process.catMETsPfMva.setUnclusteredEn = cms.bool(False)
    ## process.catMETsPfMva.setJetMETSyst = cms.bool(False)
    
