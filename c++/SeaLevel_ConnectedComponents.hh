#ifndef _SEALEVEL_CONNECTEDCOMPONENTS_H_
#define _SEALEVEL_CONNECTEDCOMPONENTS_H_

#include <vector>

#include "FillingAlg_ConnectedComponents.hh"

class SeaLevelCC : public FillingAlgCC {
public:
  SeaLevelCC(unsigned int n_rows,
             unsigned int n_cols,
             double* topo,
             double* thk,
             double* floatation_level,
             double* mask_run,
             double  drho,
             double  ice_free_thickness);
  ~SeaLevelCC();
  void fill2SeaLevel(double SeaLevel);

private:
  virtual bool SinkCond(unsigned int r, unsigned int c);
  virtual void labelMap(double Level,
                        unsigned int run_number,
                        std::vector<unsigned int> &rows,
                        std::vector<unsigned int> &columns,
                        std::vector<unsigned int> &parents,
                        std::vector<unsigned int> &lengths,
                        std::vector<bool> &isOpen);
};

#endif
