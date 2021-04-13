"""
.. file:: run_dfnworks.py
   :synopsis: run file for dfnWorks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

from pydfnworks import * 

main_time = time()
DFN = create_dfn()

DFN.make_working_directory()
DFN.check_input()
DFN.create_network()

DFN.output_report()

DFN.set_flow_solver("PFLOTRAN")
DFN.mesh_network(uniform_mesh=True)

DFN.lagrit2pflotran()

restart_file = "DUMMY/dfnworks-main/examples/ade_example/dfn_restart.in"

DFN.pflotran(transient=True,restart=True,restart_file=restart_file)
DFN.parse_pflotran_vtk_python()       
DFN.pflotran_cleanup()
DFN.pflotran_cleanup(index_finish=100,filename=restart_file)
