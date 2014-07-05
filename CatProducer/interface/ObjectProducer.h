#ifndef ObjectProducer_h
#define ObjectProducer_h

// system include files
#include <memory>
#include <string>
#include <iostream>

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "DataFormats/Provenance/interface/EventID.h"
#include "FWCore/Framework/interface/EventSetup.h"
#include "FWCore/Framework/interface/ESHandle.h"
#include "FWCore/Utilities/interface/EDMException.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ParameterSet/interface/FileInPath.h"
#include "FWCore/Framework/interface/LuminosityBlock.h"

#include "FWCore/Common/interface/TriggerNames.h"
#include "DataFormats/Common/interface/TriggerResults.h"
#include "DataFormats/Common/interface/MergeableCounter.h"

#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h" 

#include "../interface/HLTAnalyzer.h"
#include "../interface/MCAnalyzer.h"
#include "../interface/MCAssociator.h"
#include "../interface/VertexAnalyzer.h"
#include "../interface/JetAnalyzer.h"
#include "../interface/GenJetAnalyzer.h"
#include "../interface/PFJetAnalyzer.h"
#include "../interface/MuonAnalyzer.h"
#include "../interface/ElectronAnalyzer.h"
#include "../interface/PhotonAnalyzer.h"
#include "../interface/METAnalyzer.h"
#include "../interface/PFMETAnalyzer.h"
#include "../interface/GenEventAnalyzer.h"
#include "../interface/NPGenEventAnalyzer.h"
#include "../interface/SpinCorrGenAnalyzer.h"

#include "CATTools/DataFormats/interface/CatRun.h"
#include "CATTools/DataFormats/interface/CatEvent.h"
#include "CATTools/DataFormats/interface/CatParticle.h"
#include "CATTools/DataFormats/interface/CatMCParticle.h"
#include "CATTools/DataFormats/interface/CatJet.h"
#include "CATTools/DataFormats/interface/CatGenJet.h"
#include "CATTools/DataFormats/interface/CatPFJet.h"
#include "CATTools/DataFormats/interface/CatLepton.h"
#include "CATTools/DataFormats/interface/CatMuon.h"
#include "CATTools/DataFormats/interface/CatElectron.h"
#include "CATTools/DataFormats/interface/CatMET.h"
#include "CATTools/DataFormats/interface/CatPFMET.h"
#include "CATTools/DataFormats/interface/CatGenEvent.h"
#include "CATTools/DataFormats/interface/CatNPGenEvent.h"
#include "CATTools/DataFormats/interface/CatSpinCorrGen.h"
#include "CATTools/DataFormats/interface/CatVertex.h"

#include "TFile.h"
#include "TTree.h"
#include "TH1.h"
#include "TClonesArray.h"

//using namespace cat;

class ObjectProducer : public edm::EDAnalyzer {
public:
	explicit ObjectProducer(const edm::ParameterSet&);
	~ObjectProducer();
	
	
private:
	virtual void beginJob() ;
	virtual void analyze(const edm::Event&, const edm::EventSetup&);
        virtual void endLuminosityBlock(const edm::LuminosityBlock&, const EventSetup&);
	virtual void endJob() ;

	edm::ParameterSet myConfig_;
	edm::ParameterSet producersNames_;
	
	int verbosity;
	std::string rootFileName_ ;
	TFile* rootFile_ ;
	TTree* eventTree_;
	TTree* runTree_;
        TH1F* tmp_;
	bool doHLT;
	bool doMC;
	bool doPDFInfo;
	bool doSignalMuMuGamma;
	bool doSignalTopTop;
	bool doPrimaryVertex;
	bool runGeneralTracks;
	bool doGenJet;
	bool doPFJet;
	bool doMuon;
	bool doElectron;
	bool doPhoton;
	bool doPFMET;
	bool doGenEvent;
	bool doNPGenEvent;
	bool doSpinCorrGen;
	bool drawMCTree;
	std::vector<std::string> vGenJetProducer;
	std::vector<std::string> vPFJetProducer;
	std::vector<std::string> vMuonProducer;
	std::vector<std::string> vElectronProducer;
	std::vector<std::string> vPhotonProducer;
        std::vector<std::string> vPFmetProducer;
        std::vector<std::string> vTrackmetProducer; 
	int nTotEvt_;
	HLTAnalyzer* hltAnalyzer_;
	CatRun* runInfos_;
	CatEvent* rootEvent;
	TClonesArray* mcParticles;
	TClonesArray* tracks;
	std::vector<TClonesArray*> vcaloJets;
	std::vector<TClonesArray*> vgenJets;
	std::vector<TClonesArray*> vpfJets;
	std::vector<TClonesArray*> vjptJets;
	std::vector<TClonesArray*> vmuons;
	std::vector<TClonesArray*> velectrons;
	std::vector<TClonesArray*> vphotons;
	TClonesArray* CALOmet;
	std::vector<TClonesArray*> vPFmets;
	std::vector<TClonesArray*> vTrackmets;
	TClonesArray* TCmet;
	TClonesArray* genEvent;
	TClonesArray* NPgenEvent;
	TClonesArray* spinCorrGen;
	TClonesArray* primaryVertex;

        bool useEventCounter_;
        std::vector<std::string> filters_;

        bool isRealData_;
};

#endif
