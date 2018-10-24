
#include "LakeLevel_ConnectedComponents.hh"

LakeLevelCC::LakeLevelCC(unsigned int n_rows, 
                         unsigned int n_cols, 
                         double* topo, 
                         double* thk, 
                         double* floatation_level, 
                         double* run_mask, 
                         double drho)
  : FillingAlgCC(n_rows, n_cols, topo, thk, floatation_level, run_mask, drho) {
  //empty
}

LakeLevelCC::~LakeLevelCC() {
  //empty
}

void LakeLevelCC::floodMap(double zMin, double zMax, double dz) {
  double lakeLevel = zMin;
  while (lakeLevel <= zMax) {
    fill2Level(lakeLevel);
    lakeLevel += dz;
  }
}
