from PhysicsTools.PatAlgos.patTemplate_cfg import *
from FWCore.ParameterSet.VarParsing import VarParsing
options = VarParsing ('python')
options.register ('runOnMC', 1,
                  VarParsing.multiplicity.singleton,
                  VarParsing.varType.bool,
                  "runOnMC")
import sys
if hasattr(sys, "argv") == True:
    options.parseArguments()
    runOnMC = options.runOnMC

postfix = "PFlow"
jetAlgo="AK5"
doSecVertex=True # for jpsi candidates

from CATTools.CatProducer.catPatSetup_cff import *
from CATTools.CatProducer.catSetup_cff import *
catPatConfig(process, runOnMC, postfix, jetAlgo)
catSetup(process, runOnMC, doSecVertex)

process.maxEvents.input = 100
process.MessageLogger.cerr.threshold = ''
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.source.fileNames = cms.untracked.vstring(
'file:/cms/home/jlee/scratch/QCD_Pt-15to3000_Tune4C_Flat_8TeV_pythia8/14085CA3-3DE1-E111-BB95-00266CF270A8.root'
)
