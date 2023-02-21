from pydfnworks import *
import os 

jobname = os.getcwd() + "/output_backbone/"
src_path = os.getcwd() + '/output_prune/' 
BACKBONE = DFNWORKS( jobname = jobname, 
                    pickle_file = src_path + 'output_prune.pkl')
BACKBONE.prune_file = src_path + "/backbone.dat"
BACKBONE.path = src_path 
BACKBONE.make_working_directory()
BACKBONE.mesh_network(prune=True)
# ## need to fix families -> aperture and perm. 
BACKBONE.dfn_flow()

print(BACKBONE.perm)
