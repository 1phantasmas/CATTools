import FWCore.ParameterSet.Config as cms

bunchCrossing  = 25
globalTag_mc   = '80X_mcRun2_asymptotic_2016_miniAODv2'
globalTag_rd   = '80X_dataRun2_Prompt_v8'
lumiJSON       = 'Cert_271036-274421_13TeV_PromptReco_Collisions16_JSON'
pileupMCmap    = '2016_25ns_SpringMC'

JetEnergyCorrection = 'Fall15_25nsV2'
JECUncertaintyFile  = 'CATTools/CatProducer/data/JEC/%s_DATA_UncertaintySources_AK4PFchs.txt'%JetEnergyCorrection

