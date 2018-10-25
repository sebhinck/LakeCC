#include "FillingAlg_ConnectedComponents.hh"
#include <vector>
#include <cmath>


FillingAlgCC::FillingAlgCC(unsigned int n_rows, 
                           unsigned int n_cols, 
                           double *topo, 
                           double *thk , 
                           double *floatation_level, 
                           double *mask_run, 
                           double drho,
                           double ice_free_thickness)
  : m_nRows(n_rows), m_nCols(n_cols), m_topo(topo), m_thk(thk), 
    m_floatation_level(floatation_level), m_mask_run(mask_run), 
    m_drho(drho), m_ice_free_thickness(ice_free_thickness) {
  //empty
}

FillingAlgCC::~FillingAlgCC() {
  //empty
}


void FillingAlgCC::fill2Level(double Level) {
  unsigned int max_items = 2 * m_nRows;
  
  std::vector<unsigned int> parents(max_items), lengths(max_items), rows(max_items), columns(max_items);
  std::vector<bool> isIceFree(max_items);
  
  for(unsigned int i = 0; i < 2; ++i) {
    parents[i]   = 0;
    lengths[i]   = 0;
    rows[i]      = 0;
    columns[i]   = 0;
    isIceFree[i] = false;
  }
    
  unsigned int run_number = 1;
    
  for (unsigned int r = 0; r < m_nRows; ++r) {
    for (unsigned int c = 0; c < m_nCols; ++c) {
      if (ForegroundCond(r, c, Level)) {
        checkForegroundPixel(c, r, SinkCond(r, c), run_number, rows, columns, parents, lengths, isIceFree);

        if (m_thk[r * m_nCols + c] <= m_ice_free_thickness) {
          isIceFree[run_number] = true;
        }

        if ((run_number + 1) == max_items) {
          max_items += m_nRows;
          parents.resize(max_items);
          lengths.resize(max_items);
          rows.resize(max_items);
          columns.resize(max_items);
          isIceFree.resize(max_items);
        }
      }
    }
  }
    
  std::vector<bool> isOpen(run_number + 1);
  
  labelRuns(run_number, parents, isIceFree, isOpen);

  labelMap(Level, run_number, rows, columns, parents, lengths, isOpen);
}

bool FillingAlgCC::SinkCond(unsigned int r, unsigned int c) {
  return (m_mask_run[r * m_nCols + c] == 1);
}

bool FillingAlgCC::ForegroundCond(unsigned int r, unsigned int c, double Level) {
  return (((m_topo[r * m_nCols + c] + (m_drho * m_thk[r * m_nCols + c])) < Level) or 
          (m_mask_run[r * m_nCols + c] > 0));
}

void FillingAlgCC::labelMap(double Level, 
                            unsigned int run_number, 
                            std::vector<unsigned int> &rows, 
                            std::vector<unsigned int> &columns, 
                            std::vector<unsigned int> &parents, 
                            std::vector<unsigned int> &lengths, 
                            std::vector<bool> &isOpen) {
  // label Lakes
  for(unsigned int k = 0; k <= run_number; ++k) {
    for(unsigned int n = 0; n < lengths[k]; ++n) {
      m_mask_run[rows[k] * m_nCols + columns[k] + n] = parents[k];
      if(parents[k] > 1 and isOpen[parents[k]]) {
        m_floatation_level[rows[k] * m_nCols + columns[k] + n] = Level;
      }
    }
  }
}


void FillingAlgCC::run_union(std::vector<unsigned int> &parents, unsigned int run1, unsigned int run2) {
  if((parents[run1] == run2) or (parents[run2] == run1)) {
    return;
  }

  while(parents[run1] != 0) {
      run1 = parents[run1];
  }

  while(parents[run2] != 0) {
      run2 = parents[run2];
  }

  if(run1 > run2) {
      parents[run1] = run2;
  }else if(run1 < run2) {
      parents[run2] = run1;
  }

}

void FillingAlgCC::setRunSink(std::vector<unsigned int> &parents, unsigned int run) {
  while(parents[run] > 1) {
    run = parents[run];
  }

  parents[run] = 1;
}

void FillingAlgCC::checkForegroundPixel(unsigned int c, 
                                        unsigned int r, 
                                        bool isSink, 
                                        unsigned int &run_number, 
                                        std::vector<unsigned int> &rows, 
                                        std::vector<unsigned int> &columns, 
                                        std::vector<unsigned int> &parents, 
                                        std::vector<unsigned int> &lengths, 
                                        std::vector<bool> &isIceFree) {
  if((c > 0) && (m_mask_run[r*m_nCols + (c-1)] > 0)) {
    // one to the left is also foreground: continue the run
    lengths[run_number] += 1;
    if(isSink) {
      setRunSink(parents, run_number);
    }
  } else {
    //one to the left is a background pixel (or this is column 0): start a new run
    unsigned int parent;
    if(isSink) {
      parent = 1;
    } else if((r > 0) and (m_mask_run[(r - 1) * m_nCols + c] > 0)) {
      //check the pixel above and set the parent
      parent = (unsigned int)m_mask_run[(r - 1) * m_nCols + c];
    } else {
      parent = 0;
    }

    run_number += 1;

    rows[run_number] = r;
    columns[run_number] = c;
    parents[run_number] = parent;
    lengths[run_number] = 1;
    isIceFree[run_number] = false;
  }

  if((r > 0) and (m_mask_run[(r - 1) * m_nCols + c] > 0)) {
    run_union(parents, (unsigned int)m_mask_run[(r - 1) * m_nCols + c], run_number);
  }
  
  m_mask_run[r * m_nCols + c] = run_number;
}


void FillingAlgCC::labelRuns(unsigned int run_number, 
                             std::vector<unsigned int> &parents, 
                             std::vector<bool> &isIceFree, 
                             std::vector<bool> &isOpen) {
  unsigned int label = 0;
  for(unsigned int k = 0; k <= run_number; ++k) {
    if(parents[k] == 0) {
      parents[k] = label;
      label += 1;
      isOpen[parents[k]] = false;
    } else {
      parents[k] = parents[parents[k]];
    }
    if(isIceFree[k]) {
      isOpen[parents[k]] = true;
    }
  }
}
