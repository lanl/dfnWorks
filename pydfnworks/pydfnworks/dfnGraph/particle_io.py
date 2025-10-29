import os
import sys
import h5py
import timeit
import multiprocessing as mp
import numpy as np
import pandas as pd
import pickle

from pydfnworks.general.logging import local_print_log

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
        local_print_log(error, 'error')


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
        local_print_log(
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
        local_print_log(
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
        local_print_log(
            f"--> Writting Particle Trajectory information Complete. Time Required {elapsed:0.2e} seconds"
        )


def gather_particle_info(particles):
    """ Gather particle information into numpy arrays.
        
        Parameters
        ----------
            particles : list
                list of particle objects

        Returns
        -------
            adv_times, md_times, total_times : array of times
            
            length : array of lengths
            
            beta : array of beta particles
            
            stuck_particles : int 
                Number of particles that do not exit the domain

        Notes
        ------
    
    """
    # Gather data
    stuck_particle_cnt = 0
    for particle in particles:
        if not particle.exit_flag:
            stuck_particle_cnt += 1

    particle_exit_cnt = len(particles) - stuck_particle_cnt

    adv_times = np.zeros(particle_exit_cnt)
    md_times = np.zeros_like(adv_times)
    total_times = np.zeros_like(adv_times)
    length = np.zeros_like(adv_times)
    beta = np.zeros_like(adv_times)

    for i, particle in enumerate(particles):
        adv_times[i] = particle.advect_time
        md_times[i] = particle.matrix_diffusion_time
        total_times[i] = particle.total_time
        length[i] = particle.length
        beta[i] = particle.beta

    return adv_times, md_times, total_times, length, beta, stuck_particle_cnt


def dump_particle_info(particles, partime_file, frac_id_file, format):
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
            
            format : string
                file format for output. Options are hdf5 (default) and ascii. 

        Returns
        -------
            stuck_particles : int 
                Number of particles that do not exit the domain

    """
    adv_times, md_times, total_times, length, beta, stuck_cnt = gather_particle_info(
        particles)

    if format == 'ascii':
        filename = f"{partime_file}.dat"
        local_print_log(f"--> Writing Data to files: {filename}")
        # Write Header
        header = "Advective time [s],Matrix Diffusion time [s],Total travel time [s],Pathline length [m],Beta (s m^-1)"
        np.savetxt(filename,
                   np.c_[adv_times, md_times, total_times, length, beta],
                   delimiter=",",
                   header=header)

        if frac_id_file:
            filename = f"{frac_id_file}.dat"
            local_print_log(f"--> Writing fractures visted to file: {filename}")
            with open(filename, "w") as fp_frac_id:
                for particle in particles:
                    for d in particle.frac_seq[:-1]:
                        fp_frac_id.write(f"{d:d},")
                    fp_frac_id.write(f"{particle.frac_seq[-1]:d}\n")

    elif format == 'hdf5':
        filename = f"{partime_file}.hdf5"
        local_print_log(f"--> Writing particle data to file: {filename}")
        with h5py.File(filename, "w") as f5file:
            dataset_name = 'Advective time [s]'
            h5dset = f5file.create_dataset(dataset_name, data=adv_times)

            dataset_name = "Matrix Diffusion time [s]"
            h5dset = f5file.create_dataset(dataset_name, data=md_times)

            dataset_name = "Total travel time [s]"
            h5dset = f5file.create_dataset(dataset_name, data=total_times)

            dataset_name = "Pathline length [m]"
            h5dset = f5file.create_dataset(dataset_name, data=length)

            dataset_name = "Beta [s m^-1]"
            h5dset = f5file.create_dataset(dataset_name, data=beta)

        if frac_id_file:
            filename = f"{frac_id_file}.hdf5"
            local_print_log(f"--> Writing fractures visted to file: {filename}")
            with h5py.File(filename, "a") as f5file:
                for particle in particles:
                    traj_subgroup = f5file.create_group(
                        f'particle-{particle.particle_number+1}')

                    dataset_name = 'fractures'
                    data = np.asarray(particle.frac_seq)
                    h5dset = traj_subgroup.create_dataset(dataset_name,
                                                          data=data,
                                                          dtype='float64')
    elif format == "pickle":
        filename = f"{partime_file}.p"
        local_print_log(f"--> Writing Data to files: {filename}")
        data_dict = {
            'Advective time [s]': adv_times,
            'Matrix Diffusion time [s]': md_times,
            'Total travel time [s]': total_times,
            'Pathline length [m]': length,
            'Beta (s/m)': beta
        }
        pickle.dump(data_dict, open(filename, "wb"))

    elif format == "pandas":
        filename = f"{partime_file}_pandas.p"
        local_print_log(f"--> Writing Data to files: {filename}")
        data_dict = {
            'Advective time [s]': adv_times,
            'Matrix Diffusion time [s]': md_times,
            'Total travel time [s]': total_times,
            'Pathline length [m]': length,
            'Beta (s/m)': beta
        }
        df = pd.from_dict(data_dict)
        df.to_pickle(filename)

    local_print_log("--> Writing Data Complete")
    return stuck_cnt


def dump_control_planes(particles, control_planes, filename, format):
    """ write control plane travel time information to files 

        Parameters
        ------------
            particles : list
                list of particle objects 

            control_planes : list
                list of control plane values

            filename : str
                Base name for file.

            format : str
                File format. Options are hdf5 (Default) and ascii
            
        Returns
        ------------
            None

        Notes
        -------------
            None
            
    """

    num_cp = len(control_planes)
    num_particles = len(particles)
    adv_times = np.zeros((num_cp, num_particles))
    total_times = np.zeros((num_cp, num_particles))
    pathline_length = np.zeros((num_cp, num_particles))
    # x1 = np.zeros((num_cp, num_particles))
    # x2 = np.zeros((num_cp, num_particles))
    
    for i, particle in enumerate(particles):
        adv_times[:, i] = particle.cp_adv_time
        total_times[:, i] = particle.cp_tdrw_time
        pathline_length[:, i] = particle.cp_pathline_length
        # x1[:,i] = particle.cp_x1
        # x2[:,i] = particle.cp_x2

    if format == "ascii":
        local_print_log(
            f'--> Writting travel times at control planes to {filename}_adv.dat & {filename}_total.dat'
        )
        header = f"{control_planes[0]},"
        for cp in control_planes[1:-1]:
            header += f"{cp},"
        header += f"{control_planes[-1]}"
        np.savetxt(f"{filename}_adv.dat",
                   adv_times,
                   delimiter=",",
                   header=header)
        np.savetxt(f"{filename}_total.dat",
                   total_times,
                   delimiter=",",
                   header=header)
        np.savetxt(f"{filename}_pathline_length.dat",
                   pathline_length,
                   delimiter=",",
                   header=header)


    elif format == "hdf5":
        local_print_log(f'--> Writting travel times at control planes to {filename}.h5')
        with h5py.File(f"{filename}.hdf5", "w") as f5file:
            dataset_name = 'control_planes'
            h5dset = f5file.create_dataset(dataset_name, data=control_planes)
            for it in range(num_cp):
                cp_subgroup = f5file.create_group(f'cp_x_{control_planes[it]}')
                dataset_name = 'adv_times'
                adv_cp = adv_times[it, :]
                h5dset = cp_subgroup.create_dataset(dataset_name,
                                                    data=adv_cp,
                                                    dtype='float64')

                dataset_name = 'total_times'
                total_cp = total_times[it, :]
                h5dset = cp_subgroup.create_dataset(dataset_name,
                                                    data=total_cp,
                                                    dtype='float64')

                dataset_name = 'pathline_length'
                pathline_cp = pathline_length[it, :]
                h5dset = cp_subgroup.create_dataset(dataset_name,
                                                    data=pathline_cp,
                                                    dtype='float64')

                # dataset_name = 'x1'
                # x_cp = x1[it, :]
                # h5dset = cp_subgroup.create_dataset(dataset_name,
                #                                     data=x_cp,
                #                                     dtype='float64')
                # dataset_name = 'x2'
                # x_cp = x2[it, :]
                # h5dset = cp_subgroup.create_dataset(dataset_name,
                #                                     data=x_cp,
                #                                     dtype='float64')


        f5file.close()
