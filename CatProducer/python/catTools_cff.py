import FWCore.ParameterSet.Config as cms

def catTool(process, runOnMC=True, useMiniAOD=True):
    bunchCrossing=25
    globaltag_run2_50ns = ["MCRUN2_74_V9A", "74X_mcRun2_startup_v2", "74X_dataRun2_reMiniAOD_v0"]
    for i in globaltag_run2_50ns:
        if i == process.GlobalTag.globaltag:
            bunchCrossing=50
            from CATTools.CatProducer.pileupWeight_cff import pileupWeightMap
            process.pileupWeight.pileupMC = pileupWeightMap["Startup2015_50ns"]

    useJECfile = True
    
    if runOnMC:
        era = "Summer15_{}nsV5_MC".format(bunchCrossing)
    else:
        era = "Summer15_{}nsV5_DATA".format(bunchCrossing)
    jecUncertaintyFile = "CATTools/CatProducer/data/Summer15_{}nsV5_DATA_UncertaintySources_AK4PFchs.txt".format(bunchCrossing)
    
    if useJECfile:
        from CondCore.DBCommon.CondDBSetup_cfi import CondDBSetup
        process.jec = cms.ESSource("PoolDBESSource",CondDBSetup,
            connect = cms.string('sqlite_fip:CATTools/CatProducer/data/'+era+'.db'),
            toGet = cms.VPSet(
                cms.PSet(
                    record = cms.string("JetCorrectionsRecord"),
                    tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PF"),
                    label= cms.untracked.string("AK4PF")),
                cms.PSet(
                    record = cms.string("JetCorrectionsRecord"),
                    tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PFchs"),
                    label= cms.untracked.string("AK4PFchs")),
                cms.PSet(
                    record = cms.string("JetCorrectionsRecord"),
                    tag = cms.string("JetCorrectorParametersCollection_"+era+"_AK4PFPuppi"),
                    label= cms.untracked.string("AK4PFPuppi")),
            )
        )
        process.es_prefer_jec = cms.ESPrefer("PoolDBESSource","jec")
        print "JEC based on", process.jec.connect

    process.catJetsPuppi.payloadName = cms.string("AK4PFchs") #temp for now
#######################################################################
## corrections when using miniAOD
    if useMiniAOD:
#######################################################################
## Hcal HBHE https://twiki.cern.ch/twiki/bin/viewauth/CMS/MissingETOptionalFiltersRun2
        process.load('CommonTools.RecoAlgos.HBHENoiseFilterResultProducer_cfi')
        process.HBHENoiseFilterResultProducer.minZeros = cms.int32(99999)

        process.HBHENoiseFilterResultProducer.IgnoreTS4TS5ifJetInLowBVRegion=cms.bool(False) 
        process.HBHENoiseFilterResultProducer.defaultDecision = cms.string("HBHENoiseFilterResultRun2Loose")
        if bunchCrossing == 50:
            process.HBHENoiseFilterResultProducer.IgnoreTS4TS5ifJetInLowBVRegion=cms.bool(True) 
            process.HBHENoiseFilterResultProducer.defaultDecision = cms.string("HBHENoiseFilterResultRun1")

        process.ApplyBaselineHBHENoiseFilter = cms.EDFilter('BooleanFlagFilter',
            inputLabel = cms.InputTag('HBHENoiseFilterResultProducer','HBHENoiseFilterResult'),
            reverseDecision = cms.bool(False))
        
        process.nEventsFiltered = cms.EDProducer("EventCountProducer")
    
        process.p += (process.HBHENoiseFilterResultProducer* #produces HBHE bools
                      process.ApplyBaselineHBHENoiseFilter*  #reject events based
                      process.nEventsFiltered)
#######################################################################
# recompute the T1 PFMET https://twiki.cern.ch/twiki/bin/view/CMS/MissingETUncertaintyPrescription
        from PhysicsTools.PatUtils.tools.runMETCorrectionsAndUncertainties import runMetCorAndUncFromMiniAOD
        runMetCorAndUncFromMiniAOD( process, isData= not runOnMC, jecUncFile=jecUncertaintyFile)
# MET without HF
        process.noHFCands = cms.EDFilter("CandPtrSelector",
                                        src=cms.InputTag("packedPFCandidates"),
                                        cut=cms.string("abs(pdgId)!=1 && abs(pdgId)!=2 && abs(eta)<3.0"))
        
        runMetCorAndUncFromMiniAOD(process, isData=not runOnMC, jecUncFile=jecUncertaintyFile, pfCandColl=cms.InputTag("noHFCands"), postfix="NoHF")
        process.catMETsNoHF = process.catMETs.clone(src = cms.InputTag("slimmedMETsNoHF"))
        ## no residuals currently available 
        process.patPFMetT1T2Corr.jetCorrLabelRes = cms.InputTag("L3Absolute")
        process.patPFMetT1T2SmearCorr.jetCorrLabelRes = cms.InputTag("L3Absolute")
        process.patPFMetT2Corr.jetCorrLabelRes = cms.InputTag("L3Absolute")
        process.patPFMetT2SmearCorr.jetCorrLabelRes = cms.InputTag("L3Absolute")
        process.shiftedPatJetEnDown.jetCorrLabelUpToL3Res = cms.InputTag("ak4PFCHSL1FastL2L3Corrector")
        process.shiftedPatJetEnUp.jetCorrLabelUpToL3Res = cms.InputTag("ak4PFCHSL1FastL2L3Corrector")
        process.patPFMetT1T2CorrNoHF.jetCorrLabelRes = cms.InputTag("L3Absolute")
        process.patPFMetT1T2SmearCorrNoHF.jetCorrLabelRes = cms.InputTag("L3Absolute")
        process.patPFMetT2CorrNoHF.jetCorrLabelRes = cms.InputTag("L3Absolute")
        process.patPFMetT2SmearCorrNoHF.jetCorrLabelRes = cms.InputTag("L3Absolute")
        process.shiftedPatJetEnDownNoHF.jetCorrLabelUpToL3Res = cms.InputTag("ak4PFCHSL1FastL2L3Corrector")
        process.shiftedPatJetEnUpNoHF.jetCorrLabelUpToL3Res = cms.InputTag("ak4PFCHSL1FastL2L3Corrector")

        del process.slimmedMETs.t01Variation
        #del process.slimmedMETs.t1Uncertainties
        del process.slimmedMETs.tXYUncForRaw
        del process.slimmedMETs.tXYUncForT1
        del process.slimmedMETsNoHF.t01Variation
        #del process.slimmedMETsNoHF.t1Uncertainties
        del process.slimmedMETsNoHF.tXYUncForRaw
        del process.slimmedMETsNoHF.tXYUncForT1
#######################################################################
# redoing puppi from miniAOD as recommended https://twiki.cern.ch/twiki/bin/view/CMS/PUPPI
        process.load('CommonTools/PileupAlgos/Puppi_cff')
        process.puppi.candName = cms.InputTag('packedPFCandidates')
        process.puppi.vertexName = cms.InputTag('offlineSlimmedPrimaryVertices')
        
        # remaking puppi jets
        from JMEAnalysis.JetToolbox.jetToolbox_cff import jetToolbox
        jetToolbox( process, 'ak4', 'ak4JetSubs', 'out', PUMethod='Puppi', miniAOD = useMiniAOD, runOnMC = True,#due to bug in jetToolbox
                    JETCorrPayload='AK4PFPuppi', JETCorrLevels = ['L1FastJet', 'L2Relative', 'L3Absolute'] )#bug-JETCorrLevels overwritten in jetToolbox
        process.patJetGenJetMatchAK4PFPuppi.matched = cms.InputTag("slimmedGenJets")
        process.patJetsAK4PFPuppi.embedGenPartonMatch = cms.bool(False)
        process.selectedPatJetsAK4PFPuppi.cut = cms.string("pt > 20")

        # remaking puppi met
        from RecoMET.METProducers.PFMET_cfi import pfMet
        process.pfMetPuppi = pfMet.clone(src = cms.InputTag('puppi'))
        process.patPfMetPuppi = process.patMETs.clone(metSource = cms.InputTag("pfMetPuppi"), addGenMET = cms.bool(False))
        process.catMETsPuppi.src = cms.InputTag("patPfMetPuppi")

        # for puppi isolation
        ## process.packedPFCandidatesWoMuon  = cms.EDFilter("CandPtrSelector", src = cms.InputTag("packedPFCandidates"), cut = cms.string("fromPV>=2 && abs(pdgId)!=13 " ) )
        ## process.particleFlowNoMuonPUPPI.candName         = 'packedPFCandidatesWoMuon'
        ## process.particleFlowNoMuonPUPPI.vertexName       = 'offlineSlimmedPrimaryVertices'
#######################################################################    
## applying new jec on the fly
        process.load("PhysicsTools.PatAlgos.producersLayer1.jetUpdater_cff")
        process.patJetCorrFactors.primaryVertices = cms.InputTag("offlineSlimmedPrimaryVertices")
        process.catJets.src = cms.InputTag("patJetsUpdated")

        ### updating puppi jet jec
        process.patJetPuppiCorrFactorsUpdated = process.patJetCorrFactorsUpdated.clone(
            payload = cms.string('AK4PFPuppi'),
            src = cms.InputTag("selectedPatJetsAK4PFPuppi"))
        
        process.patJetsPuppiUpdated = process.patJetsUpdated.clone(
            jetCorrFactorsSource = cms.VInputTag(cms.InputTag("patJetPuppiCorrFactorsUpdated")),
            jetSource = cms.InputTag("selectedPatJetsAK4PFPuppi"))
        
        process.catJetsPuppi.src = cms.InputTag("patJetsPuppiUpdated")
#######################################################################
## for egamma pid https://twiki.cern.ch/twiki/bin/viewauth/CMS/CutBasedElectronIdentificationRun2#Recipe_for_regular_users_for_74X
        from PhysicsTools.SelectorUtils.tools.vid_id_tools import DataFormat,switchOnVIDElectronIdProducer,setupAllVIDIdsInModule,setupVIDElectronSelection
        electron_ids = ['RecoEgamma.ElectronIdentification.Identification.cutBasedElectronID_Spring15_25ns_V1_cff',
                        'RecoEgamma.ElectronIdentification.Identification.heepElectronID_HEEPV60_cff',
                        'RecoEgamma.ElectronIdentification.Identification.mvaElectronID_Spring15_25ns_nonTrig_V1_cff']
        switchOnVIDElectronIdProducer(process, DataFormat.MiniAOD)
        for idmod in electron_ids:
            setupAllVIDIdsInModule(process,idmod,setupVIDElectronSelection)

        process.catElectrons.electronIDSources = cms.PSet(
            cutBasedElectronID_Spring15_25ns_V1_standalone_loose = cms.InputTag("egmGsfElectronIDs","cutBasedElectronID-Spring15-25ns-V1-standalone-loose"),
            cutBasedElectronID_Spring15_25ns_V1_standalone_medium = cms.InputTag("egmGsfElectronIDs","cutBasedElectronID-Spring15-25ns-V1-standalone-medium"),
            cutBasedElectronID_Spring15_25ns_V1_standalone_tight = cms.InputTag("egmGsfElectronIDs","cutBasedElectronID-Spring15-25ns-V1-standalone-tight"),
            cutBasedElectronID_Spring15_25ns_V1_standalone_veto = cms.InputTag("egmGsfElectronIDs","cutBasedElectronID-Spring15-25ns-V1-standalone-veto"),
            heepElectronID_HEEPV60 = cms.InputTag("egmGsfElectronIDs","heepElectronID-HEEPV60"),
            mvaEleID_Spring15_25ns_nonTrig_V1_wp80 = cms.InputTag("egmGsfElectronIDs","mvaEleID-Spring15-25ns-nonTrig-V1-wp80"),
            mvaEleID_Spring15_25ns_nonTrig_V1_wp90 = cms.InputTag("egmGsfElectronIDs","mvaEleID-Spring15-25ns-nonTrig-V1-wp90")
        )
#######################################################################    
# adding pfMVAMet https://twiki.cern.ch/twiki/bin/viewauth/CMS/MVAMet#Spring15_samples_with_25ns_50ns
# https://github.com/cms-sw/cmssw/blob/CMSSW_7_4_X/RecoMET/METPUSubtraction/test/mvaMETOnMiniAOD_cfg.py
        process.load("RecoJets.JetProducers.ak4PFJets_cfi")
        process.ak4PFJets.src = cms.InputTag("packedPFCandidates")
        process.ak4PFJets.doAreaFastjet = cms.bool(True)

    from JetMETCorrections.Configuration.DefaultJEC_cff import ak4PFJetsL1FastL2L3

    process.load("RecoMET.METPUSubtraction.mvaPFMET_cff")
    #process.pfMVAMEt.srcLeptons = cms.VInputTag("slimmedElectrons")
    process.pfMVAMEt.srcPFCandidates = cms.InputTag("packedPFCandidates")
    process.pfMVAMEt.srcVertices = cms.InputTag("offlineSlimmedPrimaryVertices")

    process.puJetIdForPFMVAMEt.jec =  cms.string('AK4PF')
    #process.puJetIdForPFMVAMEt.jets = cms.InputTag("ak4PFJets")
    process.puJetIdForPFMVAMEt.vertexes = cms.InputTag("offlineSlimmedPrimaryVertices")
    process.puJetIdForPFMVAMEt.rho = cms.InputTag("fixedGridRhoFastjetAll")

    process.pfMVAMEt.inputFileNames = cms.PSet(
        U     = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru_7_4_X_miniAOD_{}NS_July2015.root'.format(bunchCrossing)),
        DPhi  = cms.FileInPath('RecoMET/METPUSubtraction/data/gbrphi_7_4_X_miniAOD_{}NS_July2015.root'.format(bunchCrossing)),
        CovU1 = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru1cov_7_4_X_miniAOD_{}NS_July2015.root'.format(bunchCrossing)),
        CovU2 = cms.FileInPath('RecoMET/METPUSubtraction/data/gbru2cov_7_4_X_miniAOD_{}NS_July2015.root'.format(bunchCrossing))
    )
        
    process.load("PhysicsTools.PatAlgos.producersLayer1.metProducer_cfi")
    process.patMETsPfMva = process.patMETs.clone(addGenMET = cms.bool(False), metSource  = cms.InputTag("pfMVAMEt"))
    process.catMETsPfMva = process.catMETs.clone(src = cms.InputTag("patMETsPfMva"))
    
