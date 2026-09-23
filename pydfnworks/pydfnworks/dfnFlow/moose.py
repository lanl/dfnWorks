"""Launch a MOOSE application using an existing input deck."""

import os
from pathlib import Path
import shlex
import shutil
import subprocess
from time import time


def moose(self, executable=None, conda_env=None, conda_sh=None):
    """Run Falcon/MOOSE with ``self.ncpu`` MPI ranks in ``self.jobname``.

    The input deck at ``self.dfnFlow_file`` is copied into the job directory.
    Meshes, included files and other relative dependencies must already be
    available there. No mesh conversion or output parsing is performed.

    Optional arguments override MOOSE_EXE, MOOSE_CONDA_ENV and MOOSE_CONDA_SH.
    Defaults are ~/projects/falcon/falcon-opt, falcon-moose and
    ~/miniforge/etc/profile.d/conda.sh, respectively. Environment preparation
    takes place only in a child Bash shell. Solver output streams to the caller;
    setup or solver failures raise subprocess.CalledProcessError.
    """
    if self.flow_solver != "MOOSE":
        raise ValueError("moose() requires flow_solver='MOOSE'")
    if not self.dfnFlow_file:
        raise ValueError("MOOSE requires dfnFlow_file pointing to an input deck")
    if isinstance(self.ncpu, bool) or int(self.ncpu) != self.ncpu or self.ncpu < 1:
        raise ValueError("MOOSE requires ncpu to be a positive integer")

    source = Path(self.dfnFlow_file).expanduser().resolve(strict=True)
    job = Path(self.jobname).expanduser().resolve(strict=True)
    executable = Path(executable or os.environ.get(
        "MOOSE_EXE", "~/projects/falcon/falcon-opt")).expanduser().resolve(strict=True)
    conda_sh = Path(conda_sh or os.environ.get(
        "MOOSE_CONDA_SH", "~/miniforge/etc/profile.d/conda.sh"
    )).expanduser().resolve(strict=True)
    conda_env = conda_env or os.environ.get("MOOSE_CONDA_ENV", "falcon-moose")
    if not source.is_file() or not conda_sh.is_file():
        raise ValueError("MOOSE input deck and Conda setup must be files")
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError(f"MOOSE executable is not executable: {executable}")
    if not job.is_dir():
        raise ValueError(f"MOOSE job directory does not exist: {job}")

    destination = job / source.name
    if not destination.exists() or not os.path.samefile(source, destination):
        shutil.copy2(source, destination)
    self.local_dfnFlow_file = destination.name

    # Positional arguments keep paths and environment names out of shell code.
    # Login initialization makes the cluster's module command available.
    script = r"""
set -e
if type module >/dev/null 2>&1; then
    module purge
fi
unset -f mpirun 2>/dev/null || true
unset LD_LIBRARY_PATH
source "$1"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
conda activate "$2"
exec mpiexec -n "$3" "$4" -i "$5"
"""
    command = ["bash", "-lc", script, "dfnworks-moose", str(conda_sh),
               conda_env, str(int(self.ncpu)), str(executable), destination.name]
    self.print_log("--> Running MOOSE: " + shlex.join(
        ["mpiexec", "-n", str(int(self.ncpu)), str(executable), "-i", destination.name]))
    started = time()
    try:
        subprocess.run(command, cwd=str(job), check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        self.print_log(f"MOOSE launch failed: {error}", "warning")
        raise
    self.print_log(f"MOOSE Complete. Time Required {time() - started} Seconds")
