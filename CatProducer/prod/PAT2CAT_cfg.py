from CATTools.CatProducer.catTemplate_cfg import *
## some options
doSecVertex=True # for jpsi candidates
    
## setting up arguements
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('python')
options.register('runOnMC', True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "runOnMC: 1  default")
options.register('useMiniAOD', True, VarParsing.multiplicity.singleton, VarParsing.varType.bool, "useMiniAOD: 1  default")
options.register('globalTag', '', VarParsing.multiplicity.singleton, VarParsing.varType.string, "globalTag: 1  default")

options.parseArguments()
runOnMC = options.runOnMC
useMiniAOD = options.useMiniAOD # Aren't we using miniAOD always? (either of miniAOD - > CAT or AOD -> miniAOD -> CAT) 
globalTag = options.globalTag

if globalTag:
    process.GlobalTag.globaltag = cms.string(globalTag)

from CATTools.CatProducer.patTools_cff import *
patTool(process, runOnMC, useMiniAOD)

from CATTools.CatProducer.catTools_cff import *
catTool(process, runOnMC, doSecVertex, useMiniAOD)

from CATTools.CatProducer.catEventContent_cff import *
process.out.outputCommands = catEventContent
if runOnMC:
    process.out.outputCommands.extend(catEventContentMC)
    if not useMiniAOD:
        process.out.outputCommands.extend(catEventContentAODMC)

process.maxEvents.input = options.maxEvents

# better to have a default file here for test purpose
process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
       # at CERN
       '/store/caf/user/tjkim/mc/Phys14DR/TTJets_MSDecaysCKM_central_Tune4C_13TeV-madgraph-tauola/MINIAODSIM/PU4bx50_PHYS14_25_V1-v1/00000/069C95E6-4E7F-E411-AA3F-002618943869.root'
       # to be added at KISTI
       # '',
    )
)

if options.inputFiles:
    process.source.fileNames = options.inputFiles
#pat input files are removed because it would not work if useMiniAOD is on.    
 
print "runOnMC =",runOnMC,"and useMiniAOD =",useMiniAOD
print "process.GlobalTag.globaltag =",process.GlobalTag.globaltag

## to suppress the long output at the end of the job
process.MessageLogger.cerr.threshold = ''
if options.maxEvents < 0:
    process.MessageLogger.cerr.FwkReport.reportEvery = 1000
process.options.wantSummary = True 
