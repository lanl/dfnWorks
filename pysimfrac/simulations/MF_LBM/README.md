This MF_LBM handshake demonstrates the construction of a fracture and the submission of
an MF_LBM simulation on a single GPU.  In order to run the handshake the MF_LBM code 
(https://github.com/lanl/MF-LBM) must be compiled and the path to executable included
in MF_LBM_Handshake.py.  In addition the 'readwritefortran.f90' program must be compiled 
to generate the fortran executable for converting the fortran geometry.  To do so navigate 
to the folder and run the following command with gfortran or other fortran compiler:
 
gfortran -ffree-line-length-240 readwritefortran.f90 


