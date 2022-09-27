import os
import sys
import h5py
import timeit
import multiprocessing as mp
import numpy as np


def dump_trajectory(particle):
    """ Write particle trajectory to h5 file named trajectories/trajectory_{particle.particle_number+1} 
    
    Parameters
    ---------------
        particle : object
            particle object from graph_transport

    Returns
    ---------------
        None

    Notes
    ----------------
        The directory 'trajectories' must exist in current path
    
    """

    if os.path.isdir('trajectories'):
        with h5py.File(
                f"trajectories/trajectory-{particle.particle_number+1}.hdf5",
                "w") as f5file:
            dataset_name = 'velocity'
            data = np.asarray(particle.velocity)
            h5dset = f5file.create_dataset(dataset_name, data=data)

            dataset_name = 'times'
            data = np.asarray(particle.velocity)
            h5dset = f5file.create_dataset(dataset_name, data=data)

            dataset_name = 'length'
            data = np.asarray(particle.lengths)
            h5dset = f5file.create_dataset(dataset_name, data=data)

            dataset_name = 'fractures'
            data = np.asarray(particle.frac_seq)
            h5dset = f5file.create_dataset(dataset_name, data=data)

            dataset_name = 'coords'
            data = np.asarray(particle.coords)
            h5dset = f5file.create_dataset(dataset_name, data=data)
        f5file.close()

    else:
        error = "Error. Output directorty 'trajectories' not in current path.\nExiting"
        sys.stderr.write(error)
        sys.exit(1)


def dump_trajectories(particles, num_cpu, single_file=True):
    """ Write particle trajectories to h5 files 

    Parameters
    ---------------
        particle : list
            list of particle objects from graph_transport
        num_cpu : int
            number of processors requested for io
        single_file : boolean
            If true, all particles are written into a single h5 file. If false, each particle gets an individual file. 

    Returns
    ---------------
        None

    Notes
    ----------------
        None
    """
    if single_file:
        print(
            "--> Writting particle trajectories into file 'trajectories.hdf5'")
        with h5py.File(f"trajectories.hdf5", "a") as f5file:
            for particle in particles:
                traj_subgroup = f5file.create_group(
                    f'particle_{particle.particle_number+1}')

                dataset_name = 'velocity'
                data = np.asarray(particle.velocity)
                h5dset = traj_subgroup.create_dataset(dataset_name,
                                                      data=data,
                                                      dtype='float64')

                dataset_name = 'times'
                data = np.asarray(particle.velocity)
                h5dset = traj_subgroup.create_dataset(dataset_name,
                                                      data=data,
                                                      dtype='float64')

                dataset_name = 'length'
                data = np.asarray(particle.lengths)
                h5dset = traj_subgroup.create_dataset(dataset_name,
                                                      data=data,
                                                      dtype='float64')

                dataset_name = 'fractures'
                data = np.asarray(particle.frac_seq)
                h5dset = traj_subgroup.create_dataset(dataset_name,
                                                      data=data,
                                                      dtype='float64')

                dataset_name = 'coords'
                data = np.asarray(particle.coords)
                h5dset = traj_subgroup.create_dataset(dataset_name,
                                                      data=data,
                                                      dtype='float64')
        f5file.close()

    else:
        print(
            "--> Writting individual particle trajectories into directory 'trajectories'"
        )

        if not os.path.isdir('trajectories'):
            os.mkdir('trajectories')
        tic = timeit.default_timer()
        pool = mp.Pool(num_cpu)
        particles = pool.map(dump_trajectory, particles)
        pool.close()
        pool.join()
        pool.terminate()
        elapsed = timeit.default_timer() - tic
        print(
            f"--> Writting Particle Trajectory information Complete. Time Required {elapsed:0.2e} seconds"
        )


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