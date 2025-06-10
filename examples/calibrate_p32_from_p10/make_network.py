# '''
# This examples shows one method to calibirate p32 using p10 data
# A fake well is put into the center of the domain.
# We then create a network with a p32 value and count the number of fractures that intersect that well
# We then use a root finding method to find the p32 value that provides the 
# desired p10 value. 
# this can take a while, in practice. 
# '''


from pydfnworks import *
import os
from scipy.optimize import minimize_scalar

p32 = 1.4568217933106986 ## calibrated value

src_path = os.getcwd()
jobname = f"{src_path}/output"

DFN = DFNWORKS(jobname,
            ncpu=8)

DFN.params['domainSize']['value'] = [50, 50, 50]
DFN.params['h']['value'] = 1
DFN.params['orientationOption']['value'] = 1
DFN.params['stopCondition']['value'] = 1
DFN.params['seed']['value'] = 6969420
DFN.params['boundaryFaces']['value'] = [0, 0, 0, 0, 1, 1]
DFN.params['ignoreBoundaryFaces']['value'] = True

DFN.params['disableFram']['value'] = True 

DFN.add_user_fract(shape='rect',
                radii=25.0,
                aspect_ratio=0.001,
                translation=[0, 0, 0],
                normal_vector=[1, 0, 0],
                permeability=1.0e-12)

log_mu = 0.01
log_sigma  =  0.75

DFN.add_fracture_family(shape="rect",
                        distribution="log_normal",
                        log_mean=1.59,
                        log_std= 0.15,
                        min_radius=1.0,
                        max_radius=10.0,
                        kappa=8,
                        p32=p32,
                        aspect=1.0,
                        trend=231,
                        plunge=41,
                        hy_variable='aperture',
                        hy_function="log-normal",
                        hy_params={"mu":  log_mu, "sigma":log_sigma}
                        )

DFN.add_fracture_family(shape="rect",
                        distribution="log_normal",
                        log_mean=1.59,
                        log_std= 0.15,
                        min_radius=1.0,
                        max_radius=10.0,
                        kappa=9.0,
                        p32=p32,
                        aspect=1.0,
                        trend=40,
                        plunge=46,
                        hy_variable='aperture',
                        hy_function="log-normal",
                        hy_params={"mu":  log_mu, "sigma": log_sigma}
                        )


DFN.make_working_directory(delete=True)
DFN.check_input()
DFN.create_network()
DFN.dump_hydraulic_values()

G = DFN.create_graph('fracture', 'top', 'bottom')
well_intersections = len([n for n in G.neighbors(1)])
p10 = well_intersections / DFN.params['domainSize']['value'][2]


DFN.output_report()
DFN.mesh_network()

print(p10)