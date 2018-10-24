#ifndef _LAKELEVEL_CONNECTEDCOMPONENTS_H_
#define _LAKELEVEL_CONNECTEDCOMPONENTS_H_

#include <vector>

#include "FillingAlg_ConnectedComponents.hh"

class LakeLevelCC : public FillingAlgCC {
public:
  LakeLevelCC(unsigned int n_rows, 
              unsigned int n_cols, 
              double* topo, 
              double* thk, 
              double* floatation_level, 
              double* run_mask, 
              double  drho);
  ~LakeLevelCC();
  void floodMap(double zMin, double zMax, double dz);
};

#endif
