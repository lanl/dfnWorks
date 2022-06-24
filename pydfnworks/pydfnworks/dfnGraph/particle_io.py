import sys


def prepare_output_files(partime_file, frac_id_file):
    """ opens the output files partime_file and frac_id_file and writes the
        header for each

        Parameters
        ----------

            partime_file : string
                name of file to  which the total travel times and lengths will be written for each particle

            frac_id_file : string
                name of file to which detailed information of each particle's travel will be written

        Returns
        -------
            None
    """

    try:
        with open(partime_file, "w") as fp_partime:
            fp_partime.write(
                "# Total Advective time (s), Total diffusion time (s), Total travel time (Adv.+Diff) (s),total pathline distance (m)\n"
            )
    except:
        error = f"Error: Unable to open supplied partime_file file {partime_file}\n"
        sys.stderr.write(error)
        sys.exit(1)

    try:
        with open(frac_id_file, "w") as fp_frac_id:
            fp_frac_id.write("# List of fractures that a particle visits\n")
            #f2.write(
            #    "# Line has (n+n+n+n) entries, consisting of all frac_ids (from 0), advective times (s), advective+diffusion times (s), advection dist covered (m)\n"
            #)
    except:
        error = f": Unable to open supplied frac_id_file file {frac_id_file}\n".format(
            frac_id_file)
        sys.stderr.write(error)
        sys.exit(1)


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
            pfailcount : int 
                Number of particles that do not exit the domain

        """

    prepare_output_files(partime_file, frac_id_file)

    fp_partime = open(partime_file, "a")
    fp_frac_id = open(frac_id_file, "a")

    pfailcount = 0

    for particle in particles:
        if particle.exit_flag:
            fp_partime.write(
                f"{particle.advect_time:.12e},{particle.matrix_diffusion_time:.12e},{particle.total_time:.12e},{particle.length:.12e}\n"
            )
            frac_seq = sorted(set(particle.frac_seq),
                              key=particle.frac_seq.index)
            for d in frac_seq:
                fp_frac_id.write(f"{d:d},")
            fp_frac_id.write("\n")
        else:
            pfailcount += 1

    fp_partime.close()
    fp_frac_id.close()
    return pfailcount


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
