#ifndef CATTools_GenWeights_H
#define CATTools_GenWeights_H

#include <vector>
#include <string>

// Define typedefs for convenience
namespace cat {
  class GenWeights;
}

namespace cat {

class GenWeightInfo {
public:
  GenWeightInfo() {};
  virtual ~GenWeightInfo() {};

  typedef std::vector<float> vfloat;
  typedef std::vector<std::string> vstring;
  typedef std::vector<unsigned short> vushort;

  int nGroups() const { return names_.size(); }
  std::string name(int i) const { return names_.at(i); }
  std::string combineMethod(int i) const { return combineMethods_.at(i); }
  vstring params(int i) const { return params_.at(i); }
  vushort keys(int i) const { return keys_.at(i); }

  int print() const;

  void addWeightGroup(const std::string name, const std::string combineBy, const vstring params, const vushort keys);

  enum KnownTypes { NONE=-1, Nominal, PDF, ScaleUp, ScaleDown };
  static KnownTypes toKnownType(std::string typeName);

private:
  vstring names_;
  vstring combineMethods_;
  std::vector<vstring> params_;
  std::vector<vushort> keys_;

};

class GenWeights {
public:
  GenWeights();
  virtual ~GenWeights() {};

  // Getters
  float genWeight() const { return genWeight_; }
  float lheWeight() const { return lheWeight_; }
  std::vector<float> weights() const { return weights_; };

  int id1() const { return id1_; }
  int id2() const { return id2_; }
  float x1() const { return x1_; }
  float x2() const { return x2_; }
  float qScale() const { return qScale_; }

  // Setters
  void setInfo(const int id1, const int id2, const float x1, const float x2, const float qScale);

  void setGenWeight(const float w) { genWeight_ = w; }
  void setLHEWeight(const float w) { lheWeight_ = w; }
  void addWeight(const float w) { weights_.push_back(w); }

  // Dummies to be removed
  std::vector<float> scaleUpWeights() const { return std::vector<float>(); };
  std::vector<float> scaleDownWeights() const { return std::vector<float>(); };
  std::vector<float> pdfWeights() const { return std::vector<float>(); };
  std::vector<float> otherWeights() const { return std::vector<float>(); };

private:
  int id1_, id2_;
  float x1_, x2_, qScale_;

  float genWeight_, lheWeight_;
  std::vector<float> weights_;

};

}

#endif
