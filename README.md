CATTools
========

for cms analysis

First of all, Please **fork** CATTools repositories at GitHUB.

Test file : catTuple.root can be found in https://www.dropbox.com/s/40tvwebdv6g0x1m/catTuple.root?dl=0
```bash
scram p -n cat CMSSW CMSSW_5_3_22_patch1
cd cat/src
cmsenv
git-cms-addpkg EgammaAnalysis/ElectronTools
cd EgammaAnalysis/ElectronTools/data
cat download.url | xargs wget
cd $SRT_CMSSW_BASE_SCRAMRTDEL/src
git clone https://github.com/geonmo/CATTools.git
git clone git@github.com:$USER/CATTools.git
git checkout CMSSW_5_3_22
scram b -j 8

cmsRun $SRT_CMSSW_BASE_SCRAMRTDEL/src/CATTools/CatProducer/test/runCatupling.py

```
