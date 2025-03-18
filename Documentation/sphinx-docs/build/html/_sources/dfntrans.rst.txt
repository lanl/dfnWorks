.. _dfntrans-chapter:


dfnTrans
============


dfnTrans is a method for resolving solute transport using control volume flow
solutions obtained from dfnFlow on the unstructured mesh generated using dfnGen.
We adopt a Lagrangian approach and represent a non-reactive conservative solute
as a collection of indivisible passive tracer particles. Particle tracking
methods (a) provide a wealth of information about the local flow field, (b) do
not suffer from numerical dispersion, which is inherent in the discretizations
of advection–dispersion equations, and (c) allow for the computation of each
particle trajectory to be performed in an intrinsically parallel fashion if
particles are not allowed to interact with one another or the fracture network.
However, particle tracking on a DFN poses unique challenges that arise from (a)
the quality of the flow solution, (b) the unstructured mesh representation of
the DFN, and (c) the physical phenomena of interest. The flow solutions obtained
from dfnFlow are locally mass conserving, so the particle tracking method does
not suffer from the problems inherent in using Galerkin finite element codes. 

dfnTrans starts from  reconstruction of local velocity field: Darcy fluxes
obtained using dfnFlow are used to reconstruct the local velocity field, which
is used for particle tracking on the DFN. Then, Lagrangian transport simulation
is used to determine pathlines through the network and simulate transport. It is
important to note that dfnTrans itself only solves for advective transport, but
effects of longitudinal dispersion and matrix diffusion, sorption, and other
retention processes are easily incorporated by post-processing particle
trajectories. 

The detailed description of dfnTrans algorithm and implemented
methodology is in `Makedonska, N., Painter, S. L., Bui, Q. M., Gable, C. W., &
Karra, S. (2015). Particle tracking approach for transport in three-dimensional
discrete fracture networks. Computational Geosciences, 19(5), 1123-1137.
<http://link.springer.com/article/10.1007/s10596-015-9525-4>`_


Documentation
--------------
Doxygen_

.. _Doxygen: dfnTrans_docs/index.html

