"""
MOOSE flow solver interface for dfnWorks
========================================

Setup
-----
Add the MOOSE paths to ~/.dfnworksrc (JSON) alongside the other dfnWorks
dependencies:

    {
        ...
        "MOOSE_EXE": "/path/to/falcon/falcon-opt",
        "MOOSE_ENV_SH": "/path/to/moose-env.sh"
    }

MOOSE_EXE    : (required) MOOSE application executable, e.g., Falcon.
MOOSE_ENV_SH : (optional) shell script sourced before the run to load the
               compiler / MPI modules MOOSE was built with. Leave it out if
               MOOSE runs in your current environment (e.g., a conda install).

Both paths may use ~ and are checked by define_paths() when the DFN object is
created. They can also be set as environment variables instead of in
~/.dfnworksrc.

Usage
-----
    src_path = os.getcwd()
    DFN = DFNWORKS(jobname, ncpu=4, flow_solver="MOOSE",
                   dfnFlow_file=f"{src_path}/input.i")
    ...

dfnFlow_file must be an absolute path: dfnWorks changes into jobname before
the flow solver runs, so a relative path will not be found.
    DFN.mesh_network()   # writes full_mesh.exo for MOOSE
    DFN.dfn_flow()       # calls moose()

The input deck is copied into jobname and run there as

    mpiexec -n ncpu -bind-to core $MOOSE_EXE -i input.i --n-threads=1

in a login bash shell, with one OpenMP/OpenBLAS thread per MPI rank.
"""

import os
import sys
import shutil
import subprocess
from time import time


def moose(self):
    """Run MOOSE

    Parameters
    ----------
        self : object
            DFN Class

    Returns
    -------
        None

    Notes
    -----
    Runs the executable set by MOOSE_EXE in ~/.dfnworksrc. If MOOSE_ENV_SH is
    set, that script is sourced first to load modules / MPI.
    See https://mooseframework.inl.gov/ for details about MOOSE

    """
    self.print_log("--> Running MOOSE")
    if self.flow_solver != "MOOSE":
        error = "Error. Incorrect flow solver requested\n"
        self.print_log(error, 'error')
        sys.exit(1)

    try:
        shutil.copy(self.dfnFlow_file, self.jobname)
    except:
        error = f"--> Error copying MOOSE input file: {self.dfnFlow_file}"
        self.print_log(error, 'error')
        sys.exit(1)

    tic = time()
    # One thread per MPI rank, each rank bound to its own core
    cmd = "export OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 && " \
          f"mpiexec -n {self.ncpu} -bind-to core {os.environ['MOOSE_EXE']} " \
          f"-i {self.local_dfnFlow_file} --n-threads=1"
    if os.environ.get('MOOSE_ENV_SH'):
        cmd = f"source {os.environ['MOOSE_ENV_SH']} && {cmd}"
    self.print_log(f"--> Running: {cmd}")
    # Login shell (-l) so the cluster's module command is available
    status = subprocess.call(['bash', '-lc', cmd])
    if status != 0:
        error = f"Error. MOOSE failed with exit code {status}\n"
        self.print_log(error, 'error')
        sys.exit(1)
    self.print_log('=' * 80)
    self.print_log("MOOSE Complete")
    elapsed = time() - tic
    self.print_log(f"Time Required {elapsed} Seconds")
    self.print_log('=' * 80)
