#include <stddef.h>
#include<cmath>

#include "SeaLevel_ConnectedComponents.hh"

SeaLevelCC::SeaLevelCC(unsigned int n_rows,
                       unsigned int n_cols,
                       double* topo,
                       double* thk,
                       double* floatation_level,
                       double* mask_run,
                       double drho,
                       double ice_free_thickness)
  : FillingAlgCC(n_rows, n_cols, topo, thk, floatation_level, mask_run, drho, ice_free_thickness) {
  //empty
}

SeaLevelCC::~SeaLevelCC() {
  //empty
}

void SeaLevelCC::fill2SeaLevel(double SeaLevel) {
  fill2Level(SeaLevel);
}

bool SeaLevelCC::SinkCond(unsigned int r, unsigned int c) {
  return (m_mask_run[r * m_nCols + c] == 1);
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
