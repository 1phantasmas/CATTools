#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDProducer.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/Common/interface/Association.h"
#include "DataFormats/Common/interface/RefToPtr.h"

#include "DataFormats/PatCandidates/interface/Jet.h"
#include "CATTools/DataFormats/interface/Jet.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidate.h"
#include "DataFormats/ParticleFlowCandidate/interface/PFCandidateFwd.h"
#include "CommonTools/UtilAlgos/interface/StringCutObjectSelector.h"
#include "RecoEcal/EgammaCoreTools/interface/EcalClusterLazyTools.h"

#include "CondFormats/JetMETObjects/interface/JetCorrectionUncertainty.h"
#include "CondFormats/JetMETObjects/interface/JetCorrectorParameters.h"
#include "JetMETCorrections/Objects/interface/JetCorrectionsRecord.h"

using namespace edm;
using namespace std;

namespace cat {

  class CATJetProducer : public edm::EDProducer {
  public:
    explicit CATJetProducer(const edm::ParameterSet & iConfig);
    virtual ~CATJetProducer() { }

    virtual void produce(edm::Event & iEvent, const edm::EventSetup & iSetup);

    bool checkPFJetId(const pat::Jet & jet);
    void getJER(const double jetEta, double& cJER, double& cJERUp, double& cJERDn) const;

    std::vector<const reco::Candidate *> getAncestors(const reco::Candidate &c);
    bool hasBottom(const reco::Candidate &c);
    bool hasCharm(const reco::Candidate &c);
    bool decayFromBHadron(const reco::Candidate &c);
    bool decayFromCHadron(const reco::Candidate &c);
    const reco::Candidate* lastBHadron(const reco::Candidate &c);
    const reco::Candidate* lastCHadron(const reco::Candidate &c);

  private:
    edm::InputTag src_;

    const std::vector<std::string> btagNames_;
    std::string uncertaintyTag_, payloadName_;
    bool runOnMC_;

  };

} // namespace

cat::CATJetProducer::CATJetProducer(const edm::ParameterSet & iConfig) :
  src_(iConfig.getParameter<edm::InputTag>("src")),
  btagNames_(iConfig.getParameter<std::vector<std::string> >("btagNames")),
  runOnMC_(iConfig.getParameter<bool>("runOnMC"))
{
  produces<std::vector<cat::Jet> >();
  //uncertaintyTag_    = iConfig.getParameter<std::string>("UncertaintyTag");
}

void 
cat::CATJetProducer::produce(edm::Event & iEvent, const edm::EventSetup & iSetup) {

  Handle<View<pat::Jet> > src; iEvent.getByLabel(src_, src);

  edm::Handle<edm::ValueMap<float> > pileupID;
  iEvent.getByLabel("puJetMva","full53xDiscriminant",pileupID);
  const edm::ValueMap<float>& puIdMap = *pileupID;

  edm::Handle<edm::ValueMap<float> > pileupIDCHS;
  iEvent.getByLabel("puJetMvaChs","fullDiscriminant",pileupIDCHS);
  const edm::ValueMap<float>& puIdChsMap = *pileupIDCHS;

  edm::ESHandle<JetCorrectorParametersCollection> JetCorParColl;
  iSetup.get<JetCorrectionsRecord>().get("AK5PF",JetCorParColl); 
  JetCorrectorParameters const & JetCorPar = (*JetCorParColl)["Uncertainty"];
  JetCorrectionUncertainty *jecUnc = new JetCorrectionUncertainty(JetCorPar);

  auto_ptr<vector<cat::Jet> >  out(new vector<cat::Jet>());
  int j = 0;
  for (const pat::Jet &aPatJet : *src) {
    bool looseId = checkPFJetId( aPatJet );
    cat::Jet aJet(aPatJet);

    edm::Ref<View<pat::Jet>> patJetRef(src,j);
    aJet.setPileupJetId( puIdMap[patJetRef] );
    aJet.setPileupJetIdChs( puIdChsMap[patJetRef] );
    
    jecUnc->setJetEta(aJet.eta());
    jecUnc->setJetPt(aJet.pt()); // here you must use the CORRECTED jet pt
    double unc = jecUnc->getUncertainty(true);
    aJet.setShiftedEnUp( (1. + unc) );
    jecUnc->setJetEta(aJet.eta());
    jecUnc->setJetPt(aJet.pt()); // here you must use the CORRECTED jet pt
    unc = jecUnc->getUncertainty(false);
    aJet.setShiftedEnDown( (1. - unc) );

    float fJER   = 1;
    float fJERUp = 1;
    float fJERDn = 1;
    if (runOnMC_){
      // adding genJet
      aJet.setGenJetRef(aPatJet.genJetFwdRef());

      // setting JES 
      if ( aPatJet.genJet() ){
	double cJER, cJERUp, cJERDn;
	getJER(aJet.eta(), cJER, cJERUp, cJERDn);

	const double jetPt = aJet.pt();
	const double genJetPt = aPatJet.genJet()->pt();
	const double dPt = jetPt-genJetPt;

	fJER   = max(0., (genJetPt+dPt*cJER  )/jetPt);
	fJERUp = max(0., (genJetPt+dPt*cJERUp)/jetPt);
	fJERDn = max(0., (genJetPt+dPt*cJERDn)/jetPt);
      
      }
      aJet.setSmearedRes(fJER);
      aJet.setSmearedResDown(fJERDn);
      aJet.setSmearedResUp(fJERUp);

    }
    ++j;
    aJet.setLooseId( looseId );
    
    if (btagNames_.size() == 0){
      aJet.setBDiscriminators(aPatJet.getPairDiscri());
    }
    else {
      for(unsigned int i = 0; i < btagNames_.size(); i++){
	aJet.addBDiscriminatorPair(std::make_pair(btagNames_.at(i), aPatJet.bDiscriminator(btagNames_.at(i)) ));
      }
    }

    //secondary vertex b-tagging information
    if( aPatJet.hasUserFloat("vtxMass") ) aJet.setVtxMass( aPatJet.userFloat("vtxMass") );
    if( aPatJet.hasUserFloat("vtxNtracks") ) aJet.setVtxNtracks( aPatJet.userFloat("vtxNtracks") );
    if( aPatJet.hasUserFloat("vtx3DVal") ) aJet.setVtx3DVal( aPatJet.userFloat("vtx3DVal") );
    if( aPatJet.hasUserFloat("vtx3DSig") ) aJet.setVtx3DSig( aPatJet.userFloat("vtx3DSig") );

    aJet.setHadronFlavour(aPatJet.hadronFlavour());
    aJet.setPartonFlavour(aPatJet.partonFlavour());
    int partonPdgId = aPatJet.genParton() ? aPatJet.genParton()->pdgId() : 0;
    aJet.setPartonPdgId(partonPdgId);

    out->push_back(aJet);
  }

  iEvent.put(out);
}

void cat::CATJetProducer::getJER(const double jetEta, double& cJER, double& cJERUp, double& cJERDn) const{
  const double absEta = std::abs(jetEta);
  if      ( absEta < 0.5 ) { cJER = 1.079; cJERUp = 1.105; cJERDn = 1.053; }
  else if ( absEta < 1.1 ) { cJER = 1.099; cJERUp = 1.127; cJERDn = 1.071; }
  else if ( absEta < 1.7 ) { cJER = 1.121; cJERUp = 1.150; cJERDn = 1.092; }
  else if ( absEta < 2.3 ) { cJER = 1.208; cJERUp = 1.254; cJERDn = 1.162; }
  else if ( absEta < 2.8 ) { cJER = 1.254; cJERUp = 1.316; cJERDn = 1.192; }
  else if ( absEta < 3.2 ) { cJER = 1.395; cJERUp = 1.458; cJERDn = 1.332; }
  else if ( absEta < 5.0 ) { cJER = 1.056; cJERUp = 1.247; cJERDn = 0.865; }
}

bool cat::CATJetProducer::checkPFJetId(const pat::Jet & jet){
  //Loose PF Jet id
  ///https://twiki.cern.ch/twiki/bin/viewauth/CMS/JetID
  //debug
  bool out = false;
  if( (jet.neutralHadronEnergy() + jet.HFHadronEnergy() ) / jet.energy() < 0.99
      &&jet.neutralEmEnergyFraction() < 0.99
      &&jet.numberOfDaughters() > 1
      &&(jet.chargedHadronEnergyFraction() > 0 || abs(jet.eta()) > 2.4)
      &&(jet.chargedMultiplicity() > 0 || abs(jet.eta()) > 2.4)
      &&(jet.chargedEmEnergyFraction() < 0.99 || abs(jet.eta()) > 2.4)
      ) out = true;

  return out;
}

#include "FWCore/Framework/interface/MakerMacros.h"
using namespace cat;
DEFINE_FWK_MODULE(CATJetProducer);
