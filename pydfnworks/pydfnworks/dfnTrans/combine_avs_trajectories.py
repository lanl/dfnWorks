import glob
import subprocess 
import os
from pydfnworks.dfnGen.meshing.mesh_dfn.mesh_dfn_helper import run_lagrit_script

def combine_avs_trajectories(self):

    self.print_log('--> Combining Particle avs files into a single file')

    print(self.dfnTrans_params)

    os.chdir(self.jobname + os.sep +  self.dfnTrans_params["out_dir:"] + os.sep + self.dfnTrans_params["out_path:"])
    print(os.getcwd())

    particle_filenames = sorted(glob.glob("part*inp"))

    if len(particle_filenames) > 0:
        lagrit_script = ""
        for i,particle_filename in enumerate(particle_filenames):
            if i == 0:
                lagrit_script += f"""read / {particle_filename} / mo_all
                    cmo  / setatt / mo_all / imt1 / {i+1}
            """
            else:
                lagrit_script += f"""

            read / {particle_filename} / mo_tmp
            cmo  / setatt / mo_tmp / imt1 / {i+1}
            addmesh / merge / mo_all / mo_all / mo_tmp 
            cmo / delete / mo_tmp 
            """


        lagrit_script += """
        dump / all_particles.inp / mo_all 
        finish 

        """
        lagrit_filename = 'combine_avs.lgi'
        with open(lagrit_filename, 'w') as fp:
            fp.write(lagrit_script)
            fp.flush()

        run_lagrit_script(lagrit_filename)
        self.print_log('--> Particles are in all_particle.inp')
    else:
        self.print_log("--> Unable to find avs files for particles.")

    self.print_log('--> Combining Particle avs files into a single file - complete')

    os.chdir(self.jobname)
    

