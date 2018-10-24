#include <stddef.h>
#include<cmath>

#include "SeaLevel_ConnectedComponents.hh"

SeaLevelCC::SeaLevelCC(unsigned int n_rows, 
                       unsigned int n_cols, 
                       double* topo, 
                       double* thk, 
                       double* floatation_level, 
                       double drho)
  : FillingAlgCC(n_rows, n_cols, topo, thk, floatation_level, NULL, drho) {
  //Init empty mask
  m_mask_run = new double[m_nRows * m_nCols];
  for (unsigned int i = 0; i < (m_nRows * m_nCols); i++) {
    m_mask_run[i] = 0;
  }
}

SeaLevelCC::~SeaLevelCC() {
  delete [] m_mask_run;
}

void SeaLevelCC::fill2SeaLevel(double SeaLevel) {
  fill2Level(SeaLevel);
}

bool SeaLevelCC::SinkCond(unsigned int r, unsigned int c) {
  return ((m_mask_run[r * m_nCols + c] == 1) or 
          (c == 0) or (c == (m_nCols - 1)) or 
          (r == 0) or (r == (m_nRows - 1)));
}

bool SeaLevelCC::ForegroundCond(unsigned int r, unsigned int c, double Level) {
  return ((m_topo[r * m_nCols + c] + (m_drho * m_thk[r * m_nCols + c])) < Level);
}

void SeaLevelCC::labelMap(double Level, 
                          unsigned int run_number, 
                          std::vector<unsigned int> &rows, 
                          std::vector<unsigned int> &columns, 
                          std::vector<unsigned int> &parents, 
                          std::vector<unsigned int> &lengths, 
                          std::vector<bool> &isOpen) {
  // Label Ocean cells
  for(unsigned int i = 0; i < (m_nRows * m_nCols); ++i) {
    m_floatation_level[i] = Level;
  }
  
  for(unsigned int k = 0; k <= run_number; ++k) {
    for(unsigned int n = 0; n < lengths[k]; ++n) {
//       if(parents[k] == 1) {
//         m_floatation_level[rows[k] * m_nCols + columns[k] + n] = Level;
//         //m_mask_run[rows[k] * m_nCols + columns[k] + n] = 1;
//       } else {
//         //m_mask_run[rows[k] * m_nCols + columns[k] + n] = 0;
//       }
      if(parents[k] > 1) {
        m_floatation_level[rows[k] * m_nCols + columns[k] + n] = NAN;
      }
    }
  }
}
