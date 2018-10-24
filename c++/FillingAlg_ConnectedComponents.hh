#ifndef _FILLINGALG_CONNECTEDCOMPONENTS_H_
#define _FILLINGALG_CONNECTEDCOMPONENTS_H_

#include <vector>

class FillingAlgCC {
public:
  FillingAlgCC(unsigned int n_rows, 
               unsigned int n_cols, 
               double* topo, 
               double* thk, 
               double* floatation_level, 
               double* run_mask, 
               double drho);
  virtual ~FillingAlgCC();
  void fill2Level(double Level);

protected:
  unsigned int m_nRows, m_nCols;
  double *m_topo, *m_thk, *m_floatation_level;
  double m_drho;
  double *m_mask_run;
  void run_union(std::vector<unsigned int> &parents, 
                 unsigned int run1, 
                 unsigned int run2);
  void setRunSink(std::vector<unsigned int> &parents,
                  unsigned int run);
  void checkForegroundPixel(unsigned int c, unsigned int r, 
                            bool isSink, unsigned int &run_number, 
                            std::vector<unsigned int> &rows, 
                            std::vector<unsigned int> &columns, 
                            std::vector<unsigned int> &parents, 
                            std::vector<unsigned int> &lengths, 
                            std::vector<bool> &isIceFree);
  virtual void labelRuns(unsigned int run_number, 
                         std::vector<unsigned int> &parents, 
                         std::vector<bool> &isIceFree, 
                         std::vector<bool> &isOpen);
  virtual bool SinkCond(unsigned int r, 
                        unsigned int c);
  virtual bool ForegroundCond(unsigned int r, 
                              unsigned int c, 
                              double Level);
  virtual void labelMap(double Level, 
                        unsigned int run_number, 
                        std::vector<unsigned int> &rows, 
                        std::vector<unsigned int> &columns, 
                        std::vector<unsigned int> &parents, 
                        std::vector<unsigned int> &lengths, 
                        std::vector<bool> &isOpen);
};

#endif
