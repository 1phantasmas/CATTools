#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Common/interface/Association.h"
#include "DataFormats/Common/interface/RefToPtr.h"

#include "DataFormats/PatCandidates/interface/Electron.h"
#include "CATTools/DataFormats/interface/Electron.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h"
#include "CommonTools/UtilAlgos/interface/StringCutObjectSelector.h"
#include "RecoEcal/EgammaCoreTools/interface/EcalClusterLazyTools.h"

#include "DataFormats/VertexReco/interface/Vertex.h"
#include "EgammaAnalysis/ElectronTools/interface/ElectronEffectiveArea.h"

using namespace edm;
using namespace std;

namespace cat {

  class CATElectronProducer : public edm::EDProducer {
  public:
    explicit CATElectronProducer(const edm::ParameterSet & iConfig);
    virtual ~CATElectronProducer() { }

    virtual void produce(edm::Event & iEvent, const edm::EventSetup & iSetup);
    bool mcMatch( const reco::Candidate::LorentzVector& lepton, const edm::Handle<edm::View<reco::GenParticle> > & genParticles );
    bool MatchObjects( const reco::Candidate::LorentzVector& pasObj, const reco::Candidate::LorentzVector& proObj, bool exact );

  private:
    float getEffArea( float dR, float scEta );

    edm::InputTag src_;
    edm::InputTag vertexLabel_;
    edm::InputTag mcLabel_;
    edm::InputTag beamLineSrc_;
    edm::InputTag rhoLabel_;
    bool runOnMC_;

    std::vector<std::string> electronIDNames_;

  };

} // namespace

cat::CATElectronProducer::CATElectronProducer(const edm::ParameterSet & iConfig) :
  src_(iConfig.getParameter<edm::InputTag>( "src" )),
  vertexLabel_(iConfig.getParameter<edm::InputTag>( "vertexLabel" )),
  mcLabel_(iConfig.getParameter<edm::InputTag>("mcLabel")),
  beamLineSrc_(iConfig.getParameter<edm::InputTag>("beamLineSrc")),
  rhoLabel_(iConfig.getParameter<edm::InputTag>("rhoLabel")),
  runOnMC_(iConfig.getParameter<bool>("runOnMC")),
  electronIDNames_(iConfig.getParameter<std::vector<std::string> >("electronIDNames"))
{
  produces<std::vector<cat::Electron> >();
}

void 
cat::CATElectronProducer::produce(edm::Event & iEvent, const edm::EventSetup & iSetup) {
  using namespace edm;
  using namespace std;

  Handle<View<pat::Electron> > src;
  iEvent.getByLabel(src_, src);

  Handle<View<reco::GenParticle> > genParticles;
  iEvent.getByLabel(mcLabel_,genParticles);

  Handle<View<reco::Vertex> > recVtxs;
  iEvent.getByLabel(vertexLabel_, recVtxs);
  reco::Vertex pv = recVtxs->at(0);

  Handle<double> rhoHandle;
  iEvent.getByLabel(rhoLabel_, rhoHandle);
  double rhoIso = std::max(*(rhoHandle.product()), 0.0);

  
  auto_ptr<vector<cat::Electron> >  out(new vector<cat::Electron>());

  for (const pat::Electron &aPatElectron : *src){
    cat::Electron aElectron(aPatElectron);

    bool mcMatched = mcMatch( aPatElectron.p4(), genParticles );
    aElectron.setMCMatched( mcMatched );

    aElectron.setChargedHadronIso04( aPatElectron.chargedHadronIso() );
    aElectron.setNeutralHadronIso04( aPatElectron.neutralHadronIso() );
    aElectron.setPhotonIso04( aPatElectron.photonIso() );
    aElectron.setPUChargedHadronIso04( aPatElectron.puChargedHadronIso() );

    aElectron.setChargedHadronIso03( aPatElectron.userIsolation("pat::User1Iso") );
    aElectron.setNeutralHadronIso03( aPatElectron.userIsolation("pat::User2Iso") );
    aElectron.setPhotonIso03( aPatElectron.userIsolation("pat::User3Iso") );
    aElectron.setPUChargedHadronIso03( aPatElectron.userIsolation("pat::User4Iso") );

    float scEta = aPatElectron.superCluster()->eta();
    double ecalpt = aPatElectron.ecalDrivenMomentum().pt();

    double elEffArea04 = getEffArea( 0.4, scEta);
    double chIso04 = aPatElectron.chargedHadronIso();
    double nhIso04 = aPatElectron.neutralHadronIso();
    double phIso04 = aPatElectron.photonIso();
    aElectron.setrelIso(0.4, chIso04, nhIso04, phIso04, elEffArea04, rhoIso, ecalpt);

    double elEffArea03 = getEffArea( 0.3, scEta);
    double chIso03 = aPatElectron.userIsolation("pat::User1Iso");
    double nhIso03 = aPatElectron.userIsolation("pat::User2Iso");
    double phIso03 = aPatElectron.userIsolation("pat::User3Iso");
    aElectron.setrelIso(0.3, chIso03, nhIso03, phIso03, elEffArea03, rhoIso, ecalpt);
    
    aElectron.setscEta( aPatElectron.superCluster()->eta());
    double dxy = fabs(aPatElectron.gsfTrack()->dxy(pv.position()));
    aElectron.setdxy( dxy ) ;
    double dz = fabs(aPatElectron.gsfTrack()->dz(pv.position()));
    aElectron.setdz( dz ) ;

    aElectron.setrho( rhoIso) ;
    
    aElectron.setPassConversionVeto( aPatElectron.passConversionVeto() );
    aElectron.setIsGsfCtfScPixChargeConsistent( aPatElectron.isGsfCtfScPixChargeConsistent());

    if (electronIDNames_.size() == 0)
      aElectron.setElectronIDs(aPatElectron.electronIDs());

    out->push_back(aElectron);
  }
  iEvent.put(out);
}

float 
cat::CATElectronProducer::getEffArea( float dR, float scEta) 
{
  ElectronEffectiveArea::ElectronEffectiveAreaTarget electronEATarget; 
  if ( runOnMC_ ) electronEATarget = ElectronEffectiveArea::kEleEAFall11MC;
  else electronEATarget = ElectronEffectiveArea::kEleEAData2012;

  if( dR < 0.35) 
    return ElectronEffectiveArea::GetElectronEffectiveArea( ElectronEffectiveArea::kEleGammaAndNeutralHadronIso03, scEta, electronEATarget);
  else 
    return ElectronEffectiveArea::GetElectronEffectiveArea( ElectronEffectiveArea::kEleGammaAndNeutralHadronIso04, scEta, electronEATarget);
}

bool cat::CATElectronProducer::mcMatch( const reco::Candidate::LorentzVector& lepton, const edm::Handle<edm::View<reco::GenParticle> > & genParticles ){

  bool out = false;

  for (reco::GenParticleCollection::const_iterator mcIter=genParticles->begin(); mcIter != genParticles->end(); mcIter++ ) {
    int genId = mcIter->pdgId();

    if( abs(genId) != 11 ) continue;

    bool match = MatchObjects(lepton, mcIter->p4(), false);

    if( match != true) continue;

    const reco::Candidate* mother = mcIter->mother();
    while( mother != 0 ){
      if( abs(mother->pdgId()) == 23 || abs(mother->pdgId()) == 24 ) {
	out = true;
      }
      mother = mother->mother();
    }
  }

  return out;
}


bool cat::CATElectronProducer::MatchObjects( const reco::Candidate::LorentzVector& pasObj, const reco::Candidate::LorentzVector& proObj, bool exact ) {
  double proEta = proObj.eta();
  double proPhi = proObj.phi();
  double proPt = proObj.pt();
  double pasEta = pasObj.eta();
  double pasPhi = pasObj.phi();
  double pasPt = pasObj.pt();

  double dRval = deltaR(proEta, proPhi, pasEta, pasPhi);
  double dPtRel = 999.0;
  if( proPt > 0.0 ) dPtRel = fabs( pasPt - proPt )/proPt;
  // If we are comparing two objects for which the candidates should
  // be exactly the same, cut hard. Otherwise take cuts from user.
  if( exact ) return ( dRval < 1e-3 && dPtRel < 1e-3 );
  else return ( dRval < 0.025 && dPtRel < 0.025 );
}


#include "FWCore/Framework/interface/MakerMacros.h"
using namespace cat;
DEFINE_FWK_MODULE(CATElectronProducer);
