import sys


def dump_particle_info(particles, partime_file, frac_id_file):
    """ If running graph transport in parallel, this function dumps out all the
        particle information is a single pass rather then opening and closing the
        files for every particle
        
        Parameters
        ----------
            particles : list
                list of particle objects 

            partime_file : string
                name of file to  which the total travel times and lengths will be written for each particle

            frac_id_file : string
                name of file to which detailed information of each particle's travel will be written

        Returns
        -------
            stuck_particles : int 
                Number of particles that do not exit the domain

    """

    print(f"--> Writing Data to files: {partime_file}")
    with open(partime_file, "w") as fp_partime:
        # Write Header
        fp_partime.write(
            "# Total Advective time (s), Total diffusion time (s), Total travel time (Adv. + Diff.) (s), Total pathline distance (m), Beta [s/m] \n"
        )
        stuck_particles = 0
        for particle in particles:
            if particle.exit_flag:
                fp_partime.write(
                    f"{particle.advect_time:0.12e},{particle.matrix_diffusion_time:0.12e},{particle.total_time:0.12e},{particle.length:0.12e},{particle.beta:0.12e}\n"
                )
            else:
                stuck_particles += 1

    if frac_id_file is not None:
        print(f"--> Writing fractures visted to file: {frac_id_file}")
        with open(frac_id_file, "w") as fp_frac_id:
            for particle in particles:
                for d in particle.frac_seq[:-1]:
                    fp_frac_id.write(f"{d:d},")
                fp_frac_id.write(f"{particle.frac_seq[-1]:d}\n")
    print("--> Writing Data Complete")
    return stuck_particles


def dump_control_planes(particles, control_planes):
    """ write control plane travel time information to files 

        Parameters
        ------------
            particles : list
                list of particle objects 

            control_planes : list
                list of control plane values
            
        Returns
        ------------
            None
    """

    print(
        '--> Writting advective travel times at control planes to control_planes_adv.dat'
    )
    with open('control_planes_adv.dat', "w") as fp:
        fp.write(f"cp,")
        for cp in control_planes[:-1]:
            fp.write(f"{cp},")
        fp.write(f"{control_planes[-1]}\n")
        for particle in particles:
            fp.write(f"{particle.particle_number},")
            for tau in particle.cp_adv_time[:-1]:
                fp.write(f"{tau:0.12e},")
            fp.write(f"{particle.cp_adv_time[-1]:0.12e}\n")

    print(
        '--> Writting total travel times at control planes to control_planes_total.dat'
    )
    with open('control_planes_total.dat', "w") as fp:
        fp.write(f"cp,")
        for cp in control_planes[:-1]:
            fp.write(f"{cp},")
        fp.write(f"{control_planes[-1]}\n")
        for particle in particles:
            fp.write(f"{particle.particle_number},")
            for tau in particle.cp_tdrw_time[:-1]:
                fp.write(f"{tau:0.12e},")
            fp.write(f"{particle.cp_tdrw_time[-1]:0.12e}\n")
