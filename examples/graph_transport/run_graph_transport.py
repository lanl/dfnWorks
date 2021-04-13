"""
.. file:: run_graph_transport.py
   :synopsis: run file for dfnWorks 
   :version: 1.0
   :maintainer: Jeffrey Hyman, Carl Gable
.. moduleauthor:: Shriram Srinivasan <shrirams@lanl.gov>

"""


from pydfnworks import * 

DFN = create_dfn()

DFN.make_working_directory()
DFN.check_input()
DFN.create_network()
DFN.mesh_network(visual_mode=True)

pressure_in = 2*10**6
pressure_out = 10**6
G = DFN.run_graph_flow("left","right",pressure_in,pressure_out)

number_of_particles = 10**4

DFN.run_graph_transport(G,number_of_particles,"graph_partime.dat","graph_frac_sequence.dat")
