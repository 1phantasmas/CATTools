// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"

#include "CATTools/DataFormats/interface/Muon.h"
#include "CATTools/DataFormats/interface/Electron.h"
#include "CATTools/DataFormats/interface/Jet.h"
#include "CATTools/DataFormats/interface/MET.h"

#include "TopQuarkAnalysis/TopKinFitter/interface/TtFullLepKinSolver.h"

#include "CATTools/CatAnalyzer/interface/AnalysisHelper.h"
#include "DataFormats/Math/interface/deltaR.h"
#include "TTree.h"
#include "TLorentzVector.h"

using namespace std;

class TtbarDiLeptonAnalyzer : public edm::EDAnalyzer {
public:
  explicit TtbarDiLeptonAnalyzer(const edm::ParameterSet&);
  ~TtbarDiLeptonAnalyzer();

  enum {
    CH_NONE=0, CH_MUEL=1, CH_ELEL=2, CH_MUMU=3
  };

private:
  virtual void analyze(const edm::Event&, const edm::EventSetup&) override;

  typedef std::vector<const cat::Particle*> ParticlePtrs;
  typedef std::vector<const cat::Jet*> JetPtrs;

  void selectMuons(const vector<cat::Muon>& muons, ParticlePtrs& selmuons) const;
  void selectElecs(const vector<cat::Electron>& elecs, ParticlePtrs& selelecs) const;
  void selectJets(const vector<cat::Jet>& jets, const ParticlePtrs& recolep, JetPtrs& seljets) const;
  void selectBJets(const JetPtrs& jets, JetPtrs& selBjets) const;
  const reco::Candidate* getLast(const reco::Candidate* p) const;

  edm::EDGetTokenT<int> recoFiltersToken_;

  edm::EDGetTokenT<std::vector<cat::Muon> >     muonToken_;
  edm::EDGetTokenT<std::vector<cat::Electron> > elecToken_;
  edm::EDGetTokenT<std::vector<cat::Jet> >      jetToken_;
  edm::EDGetTokenT<std::vector<cat::MET> >      metToken_;
  edm::EDGetTokenT<reco::VertexCollection >   vtxToken_;
  edm::EDGetTokenT<int>          partonTop_channel_;
  edm::EDGetTokenT<vector<int> > partonTop_modes_;
  edm::EDGetTokenT<reco::GenParticleCollection > partonTop_genParticles_;

  edm::EDGetTokenT<vector<reco::GenJet>      > pseudoTop_jets_;
  edm::EDGetTokenT<vector<reco::GenJet>      > pseudoTop_leptons_;
  edm::EDGetTokenT<vector<reco::GenParticle> > pseudoTop_;
  edm::EDGetTokenT<vector<reco::GenParticle> > pseudoTop_neutrinos_;
  edm::EDGetTokenT<vector<reco::MET>         > pseudoTop_mets_;

  edm::EDGetTokenT<edm::TriggerResults> triggerBits_;
  edm::EDGetTokenT<pat::TriggerObjectStandAloneCollection> triggerObjects_;

  TTree * ttree_;
  int b_partonChannel, b_partonMode1, b_partonMode2;
  int b_pseudoTopChannel, b_pseudoTopMode1, b_pseudoTopMode2;
  int b_njet, b_nbjet, b_step, b_channel;
  bool b_lepinPhase, b_jetinPhase;
  float b_MET, b_maxweight;

  float b_lep1_pt, b_lep1_eta, b_lep1_phi;
  float b_lep2_pt, b_lep2_eta, b_lep2_phi;
  float b_ll_pt, b_ll_eta, b_ll_phi, b_ll_m;
  float b_jet_pt, b_jet_eta, b_jet_phi, b_jet_m, b_jet_CSVInclV2;
  float b_top1_pt, b_top1_eta, b_top1_phi;
  float b_top2_pt, b_top2_eta, b_top2_phi;
  float b_tri;
  int b_filtered;
  int b_is3lep;

  std::unique_ptr<TtFullLepKinSolver> solver;
  bool isTTbarMC_;
  std::vector<int> pseudoTop_modes;
  //enum TTbarMode { CH_NONE = 0, CH_FULLHADRON = 1, CH_SEMILEPTON, CH_FULLLEPTON };
  //enum DecayMode { CH_HADRON = 1, CH_MUON, CH_ELECTRON, CH_TAU_HADRON, CH_TAU_MUON, CH_TAU_ELECTRON };

  const static int NCutflow = 6;
  std::vector<std::vector<int> > cutflow_;
};
//
// constructors and destructor
//
TtbarDiLeptonAnalyzer::TtbarDiLeptonAnalyzer(const edm::ParameterSet& iConfig)
{
  recoFiltersToken_ = consumes<int>(iConfig.getParameter<edm::InputTag>("recoFilters"));

  muonToken_ = consumes<std::vector<cat::Muon> >(iConfig.getParameter<edm::InputTag>("muons"));
  elecToken_ = consumes<std::vector<cat::Electron> >(iConfig.getParameter<edm::InputTag>("electrons"));
  jetToken_  = consumes<std::vector<cat::Jet> >(iConfig.getParameter<edm::InputTag>("jets"));
  metToken_  = consumes<std::vector<cat::MET> >(iConfig.getParameter<edm::InputTag>("mets"));
  vtxToken_  = consumes<reco::VertexCollection >(iConfig.getParameter<edm::InputTag>("vertices"));

  isTTbarMC_ = iConfig.getParameter<bool>("isTTbarMC");
  if ( isTTbarMC_ ) {
    partonTop_channel_ = consumes<int>(iConfig.getParameter<edm::InputTag>("partonTop_channel"));
    partonTop_modes_   = consumes<vector<int> >(iConfig.getParameter<edm::InputTag>("partonTop_modes"));
    partonTop_genParticles_   = consumes<reco::GenParticleCollection >(iConfig.getParameter<edm::InputTag>("partonTop_genParticles"));
    pseudoTop_jets_      = consumes<vector<reco::GenJet>      >(iConfig.getParameter<edm::InputTag>("pseudoTop_jets"));
    pseudoTop_leptons_   = consumes<vector<reco::GenJet>      >(iConfig.getParameter<edm::InputTag>("pseudoTop_leptons"));
    pseudoTop_           = consumes<vector<reco::GenParticle> >(iConfig.getParameter<edm::InputTag>("pseudoTop"));
    pseudoTop_neutrinos_ = consumes<vector<reco::GenParticle> >(iConfig.getParameter<edm::InputTag>("pseudoTop_neutrinos"));
    pseudoTop_mets_      = consumes<vector<reco::MET>         >(iConfig.getParameter<edm::InputTag>("pseudoTop_mets"));
  }

  triggerBits_ = consumes<edm::TriggerResults>(iConfig.getParameter<edm::InputTag>("triggerBits"));
  triggerObjects_ = consumes<pat::TriggerObjectStandAloneCollection>(iConfig.getParameter<edm::InputTag>("triggerObjects"));

  const double tmassbegin = iConfig.getParameter<double>       ("tmassbegin");
  const double tmassend   = iConfig.getParameter<double>       ("tmassend");
  const double tmassstep  = iConfig.getParameter<double>       ("tmassstep");
  const auto   nupars     = iConfig.getParameter<vector<double> >("neutrino_parameters");

  solver.reset(new TtFullLepKinSolver(tmassbegin, tmassend, tmassstep, nupars));

  edm::Service<TFileService> fs;
  ttree_ = fs->make<TTree>("tree", "tree");
  ttree_->Branch("parton_channel", &b_partonChannel, "parton_channel/I");
  ttree_->Branch("parton_mode1", &b_partonMode1, "parton_mode1/I");
  ttree_->Branch("parton_mode2", &b_partonMode2, "parton_mode2/I");
  ttree_->Branch("pseudoTop_channel", &b_pseudoTopChannel, "pseudoTop_channel/I");
  ttree_->Branch("pseudoTop_mode1", &b_pseudoTopMode1, "pseudoTop_mode1/I");
  ttree_->Branch("pseudoTop_mode2", &b_pseudoTopMode2, "pseudoTop_mode2/I");

  ttree_->Branch("njet", &b_njet, "njet/I");
  ttree_->Branch("nbjet", &b_nbjet, "nbjet/I");
  ttree_->Branch("MET", &b_MET, "MET/F");
  ttree_->Branch("channel", &b_channel, "channel/I");
  ttree_->Branch("step", &b_step, "step/I");
  ttree_->Branch("lepinPhase", &b_lepinPhase, "lepinPhase/O");
  ttree_->Branch("jetinPhase", &b_jetinPhase, "jetinPhase/O");

  ttree_->Branch("lep1_pt", &b_lep1_pt, "lep1_pt/F");
  ttree_->Branch("lep1_eta", &b_lep1_eta, "lep1_eta/F");
  ttree_->Branch("lep1_phi", &b_lep1_phi, "lep1_phi/F");
  ttree_->Branch("lep2_pt", &b_lep2_pt, "lep2_pt/F");
  ttree_->Branch("lep2_eta", &b_lep2_eta, "lep2_eta/F");
  ttree_->Branch("lep2_phi", &b_lep2_phi, "lep2_phi/F");
  ttree_->Branch("ll_pt", &b_ll_pt, "ll_pt/F");
  ttree_->Branch("ll_eta", &b_ll_eta, "ll_eta/F");
  ttree_->Branch("ll_phi", &b_ll_phi, "ll_phi/F");
  ttree_->Branch("ll_m", &b_ll_m, "ll_m/F");
  ttree_->Branch("jet_pt", &b_jet_pt, "jet_pt/F");
  ttree_->Branch("jet_eta", &b_jet_eta, "jet_eta/F");
  ttree_->Branch("jet_phi", &b_jet_phi, "jet_phi/F");
  ttree_->Branch("jet_m", &b_jet_m, "jet_m/F");
  ttree_->Branch("jet_CSVInclV2", &b_jet_CSVInclV2, "jet_CSVInclV2/F");

  ttree_->Branch("top1_pt", &b_top1_pt, "top1_pt/F");
  ttree_->Branch("top1_eta", &b_top1_eta, "top1_eta/F");
  ttree_->Branch("top1_phi", &b_top1_pt, "top1_phi/F");
  ttree_->Branch("top2_pt", &b_top2_pt, "top2_pt/F");
  ttree_->Branch("top2_eta", &b_top2_eta, "top2_eta/F");
  ttree_->Branch("top2_phi", &b_top2_pt, "top2_phi/F");

  ttree_->Branch("tri", &b_tri, "tri/F");
  ttree_->Branch("filtered", &b_filtered, "filtered/I");
  ttree_->Branch("is3lep", &b_is3lep, "is3lep/I");

  for (int i = 0; i < NCutflow; i++) cutflow_.push_back({0,0,0,0});
}

TtbarDiLeptonAnalyzer::~TtbarDiLeptonAnalyzer()
{
  cout <<"cut flow         emu         ee         mumu"<< endl;
  for ( int i=0; i<NCutflow; ++i ) {
    cout <<"step "<< i << " "<< cutflow_[i][0] <<  " "<< cutflow_[i][1] << " " << cutflow_[i][2] << " " << cutflow_[i][3]<< endl;
  }
}

void TtbarDiLeptonAnalyzer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  b_partonChannel = -1; b_partonMode1 = -1; b_partonMode2 = -1;
  b_pseudoTopChannel = -1; b_pseudoTopMode1 = -1; b_pseudoTopMode2 = -1;
  b_MET = -1;
  b_njet = -1;
  b_nbjet = -1;
  b_channel = 0;
  b_step = -1;
  b_lepinPhase = false; b_jetinPhase = false;
  b_lep1_pt = -9; b_lep1_eta = -9; b_lep1_phi = -9;
  b_lep2_pt = -9; b_lep2_eta = -9; b_lep2_phi = -9;
  b_ll_pt = -9; b_ll_eta = -9; b_ll_phi = -9; b_ll_m = -9;
  b_jet_pt = -9; b_jet_eta = -9; b_jet_phi = -9; b_jet_m = -9; b_jet_CSVInclV2 = -9;
  b_top1_pt = -9; b_top1_eta = -9; b_top1_phi = -9;
  b_top2_pt = -9; b_top2_eta = -9; b_top2_phi = -9;
  b_tri = -9;
  b_filtered = -9; b_is3lep = -9;
  if ( isTTbarMC_ and iEvent.isRealData() ) isTTbarMC_ = false;

  // bool debug = false;
  // if (iEvent.id().event() == 312909020 || iEvent.id().event() == 255013550){
  //   debug = true;
  //   cout <<"############## debugging iEvent.id().event()" << iEvent.id().event()<<endl;
  // }
  edm::Handle<reco::VertexCollection> vertices;      iEvent.getByToken(vtxToken_, vertices);
  if (vertices->empty()){ return;} // skip the event if no PV found
  // const reco::Vertex &PV = vertices->front();
  edm::Handle<std::vector<cat::Muon> > muons;          iEvent.getByToken(muonToken_, muons);
  edm::Handle<std::vector<cat::Electron> > electrons;  iEvent.getByToken(elecToken_, electrons);
  edm::Handle<std::vector<cat::Jet> > jets;            iEvent.getByToken(jetToken_, jets);
  edm::Handle<std::vector<cat::MET> > mets;            iEvent.getByToken(metToken_, mets);

  if (isTTbarMC_){
    edm::Handle<int> partonTop_channel;
    edm::Handle<vector<int> > partonTop_modes;
    edm::Handle<reco::GenParticleCollection > partonTop_genParticles;
    iEvent.getByToken(partonTop_channel_, partonTop_channel);
    iEvent.getByToken(partonTop_modes_, partonTop_modes);
    iEvent.getByToken(partonTop_genParticles_, partonTop_genParticles);
    if ( (*partonTop_modes).size() == 0 ) {
      b_partonMode1 = 0;
      b_partonMode2 = 0;
    }
    else if ( (*partonTop_modes).size() == 1 ) { b_partonMode2 = 0; }
    else{
      b_partonChannel = *partonTop_channel;
      b_partonMode1 = (*partonTop_modes)[0];
      b_partonMode2 = (*partonTop_modes)[1];
    }

    edm::Handle<vector<reco::GenJet>      > pseudoTop_jets;
    edm::Handle<vector<reco::GenJet>      > pseudoTop_leptons;
    edm::Handle<vector<reco::GenParticle> > pseudoTop;
    edm::Handle<vector<reco::GenParticle> > pseudoTop_neutrinos;
    edm::Handle<vector<reco::MET>         > pseudoTop_mets;
    iEvent.getByToken(pseudoTop_jets_     , pseudoTop_jets);
    iEvent.getByToken(pseudoTop_leptons_  , pseudoTop_leptons);
    iEvent.getByToken(pseudoTop_          , pseudoTop);
    iEvent.getByToken(pseudoTop_neutrinos_, pseudoTop_neutrinos);
    iEvent.getByToken(pseudoTop_mets_     , pseudoTop_mets);

    if ((*pseudoTop_leptons).size() == 2){
      if (((*pseudoTop_leptons)[0].pt() > 20) && ((*pseudoTop_leptons)[1].pt() > 20) && (std::abs((*pseudoTop_leptons)[0].eta()) < 2.4) && (std::abs((*pseudoTop_leptons)[1].eta()) < 2.4)) b_lepinPhase = true;
    }

    if ((*pseudoTop_jets).size() == 2){
      if (((*pseudoTop_jets)[0].pt() > 30) && ((*pseudoTop_jets)[1].pt() > 30) && (std::abs((*pseudoTop_jets)[0].eta()) < 2.4) && (std::abs((*pseudoTop_jets)[1].eta()) < 2.4)) b_jetinPhase = true;
    }

    int mode = 0;
    pseudoTop_modes.clear();
    for (const reco::GenJet & g : *pseudoTop_leptons){
      if ( std::abs(g.pdgId()) == 13){ mode = 2; }
      else if ( std::abs(g.pdgId()) == 11){ mode = 3; }
      pseudoTop_modes.push_back(mode);
    }

    if ( pseudoTop_modes.size() < 2 ){
      for (const reco::GenParticle & g : *pseudoTop_neutrinos){
	if (std::abs(g.pdgId()) == 16){
	  pseudoTop_modes.push_back(4);
	}
      }
    }

    if ( pseudoTop_modes.size() == 0 ) { pseudoTop_modes.push_back(0); }
    if ( pseudoTop_modes.size() == 1 ) { pseudoTop_modes.push_back(0); }
    b_pseudoTopMode1 = pseudoTop_modes[0];
    b_pseudoTopMode2 = pseudoTop_modes[1];

  }

  // Store reco filter results
  edm::Handle<int> recoFiltersHandle;
  iEvent.getByToken(recoFiltersToken_, recoFiltersHandle);
  b_filtered = *recoFiltersHandle == 0 ? false : true;

  // Find leptons and sort by pT
  ParticlePtrs recolep;
  selectMuons(*muons, recolep);
  selectElecs(*electrons, recolep);
  if (recolep.size() < 2) return;
  // A lambda function to return a->pt() > b->pt()
  auto GtByPtPtr = [](const cat::Particle* a, const cat::Particle* b){return a->pt() > b->pt();};
  sort(recolep.begin(), recolep.end(), GtByPtPtr);
  const auto& recolep1 = *recolep[0];
  const auto& recolep2 = *recolep[1];

  // Determine channel
  const int pdgIdSum = std::abs(recolep1.pdgId()) + std::abs(recolep2.pdgId());
  if (pdgIdSum == 24) b_channel = CH_MUEL; // emu
  if (pdgIdSum == 22) b_channel = CH_ELEL; // ee
  if (pdgIdSum == 26) b_channel = CH_MUMU; // mumu

  // Trigger results
  edm::Handle<edm::TriggerResults> triggerBits;
  edm::Handle<pat::TriggerObjectStandAloneCollection> triggerObjects;
  iEvent.getByToken(triggerBits_, triggerBits);
  iEvent.getByToken(triggerObjects_, triggerObjects);
  const edm::TriggerNames &triggerNames = iEvent.triggerNames(*triggerBits);
  AnalysisHelper trigHelper = AnalysisHelper(triggerNames, triggerBits, triggerObjects);
  bool tri=false;

  if (b_channel == CH_ELEL and
      (trigHelper.triggerFired("HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_v") ||
       trigHelper.triggerFired("HLT_Ele23_Ele12_CaloIdL_TrackIdL_IsoVL_DZ_v")) ) tri = true;

  if (b_channel == CH_MUMU and
      (trigHelper.triggerFired("HLT_Mu17_Mu8_DZ_v") ||
       trigHelper.triggerFired("HLT_Mu17_TkMu8_DZ_v") ||
       trigHelper.triggerFired("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_DZ_v") ||
       trigHelper.triggerFired("HLT_Mu17_TrkIsoVVL_Mu8_TrkIsoVVL_v") ||
       trigHelper.triggerFired("HLT_Mu17_TrkIsoVVL_TkMu8_TrkIsoVVL_v")) ) tri = true;

  if (b_channel == CH_MUEL and
      (trigHelper.triggerFired("HLT_Mu17_TrkIsoVVL_Ele12_CaloIdL_TrackIdL_IsoVL_v") ||
       trigHelper.triggerFired("HLT_Mu8_TrkIsoVVL_Ele17_CaloIdL_TrackIdL_IsoVL_v")) ) tri = true;

  if (!tri) return;

  cutflow_[++b_step][b_channel]++;

  b_lep1_pt = recolep1.pt(); b_lep1_eta = recolep1.eta(); b_lep1_phi = recolep1.phi();
  b_lep2_pt = recolep2.pt(); b_lep2_eta = recolep2.eta(); b_lep2_phi = recolep2.phi();
  const TLorentzVector tlv_ll = recolep1.tlv()+recolep2.tlv();
  b_ll_pt = tlv_ll.Pt(); b_ll_eta = tlv_ll.Eta(); b_ll_phi = tlv_ll.Phi(); b_ll_m = tlv_ll.M();

  if (b_ll_m < 20.){
    ttree_->Fill();
    return;
  }
  if (recolep1.charge() * recolep2.charge() > 0){
    ttree_->Fill();
    return;
  }
  cutflow_[++b_step][b_channel]++;

  if (b_channel != CH_MUEL){
    if ((b_ll_m > 76) && (b_ll_m < 106)){
      ttree_->Fill();
      return;
    }
  }
  cutflow_[++b_step][b_channel]++;

  JetPtrs selectedJets, selectedBJets;
  selectJets(*jets, recolep, selectedJets);
  selectBJets(selectedJets, selectedBJets);
  const TLorentzVector met = mets->front().tlv();
  b_MET = met.Pt();
  b_njet = selectedJets.size();
  b_nbjet = selectedBJets.size();

  if (selectedJets.size() < 2){
    ttree_->Fill();
    return;
  }
  cutflow_[++b_step][b_channel]++;

  if (b_channel != CH_MUEL){
    if (b_MET < 40.){
      ttree_->Fill();
      return;
    }
  }
  cutflow_[++b_step][b_channel]++;

  if (selectedBJets.size() == 0){
    ttree_->Fill();
    return;
  }
  cutflow_[++b_step][b_channel]++;

  //  printf("selectedMuons %lu, selectedElectrons %lu, selectedJets %lu, selectedBJets %lu\n",selectedMuons.size(), selectedElectrons.size(), selectedJets.size(), selectedBJets.size() );
  /*
    for (auto jet : selectedJets) {
    TLorentzVector tlv_jet = jet.tlv();
    b_jet_pt = tlv_jet.Pt();
    b_jet_eta = tlv_jet.Eta();
    b_jet_phi = tlv_jet.Phi();
    b_jet_m = tlv_jet.M();
    b_jet_CSVInclV2 = jet.bDiscriminator("pfCombinedInclusiveSecondaryVertexV2BJetTags");
    }
  */

  ////////////////////////////////////////////////////////  KIN  /////////////////////////////////////
  //int kin=0;
  TLorentzVector top1, top2, nu1, nu2;
  double maxweight=0;
  //const cat::Jet* kinj1, * kinj2;

  const TLorentzVector recolepLV1= recolep1.tlv();
  const TLorentzVector recolepLV2= recolep2.tlv();
  for (auto jet1 = selectedJets.begin(), end = selectedJets.end(); jet1 != end; ++jet1){
    const TLorentzVector recojet1= (*jet1)->tlv();
    for (auto jet2 = next(jet1); jet2 != end; ++jet2){

      const TLorentzVector recojet2= (*jet2)->tlv();

      const double xconstraint = recolep1.px()+recolep2.px()+ recojet1.Px() + recojet2.Px() +met.Px();
      const double yconstraint = recolep1.py()+recolep2.py()+ recojet1.Py() + recojet2.Py() +met.Py();

      solver->SetConstraints(xconstraint, yconstraint);
      const auto nuSol1 = solver->getNuSolution( recolepLV1, recolepLV2 , recojet1, recojet2);
      const auto nuSol2 = solver->getNuSolution( recolepLV1, recolepLV2 , recojet2, recojet1);

      const double weight1 = nuSol1.weight;
      const double weight2 = nuSol2.weight;

      if ( weight1 > maxweight and weight1 >= weight2 ) {
        nu1 = AnalysisHelper::leafToTLorentzVector(nuSol1.neutrino);
        nu2 = AnalysisHelper::leafToTLorentzVector(nuSol1.neutrinoBar);
        maxweight = weight1;
      }
      else if ( weight2 > maxweight and weight2 >= weight1 ) {
        nu1 = AnalysisHelper::leafToTLorentzVector(nuSol2.neutrino);
        nu2 = AnalysisHelper::leafToTLorentzVector(nuSol2.neutrinoBar);
        maxweight = weight2;
      }
      else continue;

      top1 = recolepLV1+recojet1+nu1;
      top2 = recolepLV2+recojet2+nu2;
    }
  }

  b_top1_pt = top1.Pt();
  b_top1_eta = top1.Eta();
  b_top1_phi = top1.Phi();
  b_top2_pt = top2.Pt();
  b_top2_eta = top2.Eta();
  b_top2_phi = top2.Phi();

  b_maxweight = maxweight;
  //  printf("maxweight %f, top1.M() %f, top2.M() %f \n",maxweight, top1.M(), top2.M() );
  // printf("%2d, %2d, %2d, %2d, %6.2f, %6.2f, %6.2f\n", b_njet, b_nbjet, b_step, b_channel, b_MET, b_ll_mass, b_maxweight);

  ttree_->Fill();
}

const reco::Candidate* TtbarDiLeptonAnalyzer::getLast(const reco::Candidate* p) const
{
  for ( size_t i=0, n=p->numberOfDaughters(); i<n; ++i )
  {
    const reco::Candidate* dau = p->daughter(i);
    if ( p->pdgId() == dau->pdgId() ) return getLast(dau);
  }
  return p;
}

void TtbarDiLeptonAnalyzer::selectMuons(const std::vector<cat::Muon>& muons, ParticlePtrs& selmuons) const
{
  for (auto mu : muons) {
    if (mu.pt() < 20.) continue;
    if (std::abs(mu.eta()) > 2.4) continue;
    //if (!mu.isMediumMuon()) continue;
    if (!mu.isTightMuon()) continue;
    if (mu.relIso(0.4) > 0.12) continue;
    //printf("muon with pt %4.1f, POG loose id %d, tight id %d\n", mu.pt(), mu.isLooseMuon(), mu.isTightMuon());
    selmuons.push_back(&mu);
  }
}

void TtbarDiLeptonAnalyzer::selectElecs(const std::vector<cat::Electron>& elecs, ParticlePtrs& selelecs) const
{
  for (auto el : elecs) {
    if (el.pt() < 20.) continue;
    if ((std::abs(el.scEta()) > 1.4442) && (std::abs(el.scEta()) < 1.566)) continue;
    if (std::abs(el.eta()) > 2.4) continue;
    //if (!el.electronID("cutBasedElectronID-Spring15-50ns-V1-standalone-medium")) continue;
    //if (el.electronID("cutBasedElectronID-PHYS14-PU20bx25-V2-standalone-medium") == 0) continue;
    if ( !el.electronID("cutBasedElectronID-Spring15-25ns-V1-standalone-medium") ) continue;
    //if (!el.passConversionVeto()) continue;
    if (!el.isPF()) continue;

    //printf("electron with pt %4.1f\n", el.pt());
    selelecs.push_back(&el);
  }
}

void TtbarDiLeptonAnalyzer::selectJets(const vector<cat::Jet>& jets, const ParticlePtrs& recolep, JetPtrs& seljets) const
{
  seljets.clear();
  for (auto jet : jets) {
    if (jet.pt() < 30.) continue;
    if (std::abs(jet.eta()) > 2.4)	continue;
    if (!jet.LooseId()) continue;

    bool hasOverLap = false;
    for (auto lep : recolep){
      if (deltaR(jet.p4(),lep->p4()) < 0.4) hasOverLap = true;
    }
    if (hasOverLap) continue;
    // printf("jet with pt %4.1f\n", jet.pt());
    seljets.push_back(&jet);
  }
}

void TtbarDiLeptonAnalyzer::selectBJets(const JetPtrs& jets, JetPtrs& selBjets) const
{
  for (auto jet : jets) {
    if (jet->bDiscriminator("pfCombinedInclusiveSecondaryVertexV2BJetTags") < 0.605) continue;
    //printf("b jet with pt %4.1f\n", jet.pt());
    selBjets.push_back(jet);
  }
}

//define this as a plug-in
DEFINE_FWK_MODULE(TtbarDiLeptonAnalyzer);
