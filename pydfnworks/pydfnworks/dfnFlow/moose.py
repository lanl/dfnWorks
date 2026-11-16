"""Launch a MOOSE application using an existing input deck."""

import os
from pathlib import Path
import shlex
import shutil
import subprocess
from time import time


def moose(self, executable=None, env_sh=None):
    """Run Falcon/MOOSE with ``self.ncpu`` MPI ranks in ``self.jobname``.

    The input deck at ``self.dfnFlow_file`` is copied into the job directory.
    Meshes, included files and other relative dependencies must already be
    available there. No mesh conversion or output parsing is performed.

    Optional arguments override MOOSE_EXE and MOOSE_ENV_SH. Defaults are
    ~/projects/falcon-native/falcon-opt and ~/projects/moose-native-env.sh.
    The setup script must load the matching native compiler/MPI modules.
    Environment preparation
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
        "MOOSE_EXE", "~/projects/falcon-native/falcon-opt")).expanduser().resolve(strict=True)
    env_sh = Path(env_sh or os.environ.get(
        "MOOSE_ENV_SH", "~/projects/moose-native-env.sh"
    )).expanduser().resolve(strict=True)
    if not source.is_file() or not env_sh.is_file():
        raise ValueError("MOOSE input deck and native environment setup must be files")
    if not executable.is_file() or not os.access(executable, os.X_OK):
        raise ValueError(f"MOOSE executable is not executable: {executable}")
    if not job.is_dir():
        raise ValueError(f"MOOSE job directory does not exist: {job}")

    destination = job / source.name
    if not destination.exists() or not os.path.samefile(source, destination):
        shutil.copy2(source, destination)
    self.local_dfnFlow_file = destination.name

    # Positional arguments keep paths out of shell code. Login initialization
    # makes the cluster's module command available to the user's setup script.
    script = r"""
set -e
source "$1"
export OPENBLAS_NUM_THREADS=1
export OMP_NUM_THREADS=1
exec mpiexec -n "$2" -bind-to core "$3" -i "$4" --n-threads=1
"""
    command = ["bash", "-lc", script, "dfnworks-moose", str(env_sh),
               str(int(self.ncpu)), str(executable), destination.name]
    self.print_log(f"--> Native MOOSE environment: {env_sh}")
    mpi_command = shlex.join(
        ["mpiexec", "-n", str(int(self.ncpu)), "-bind-to", "core",
         str(executable), "-i", destination.name, "--n-threads=1"])
    self.print_log(f"--> Running MOOSE: {mpi_command}")
    started = time()
    try:
        subprocess.run(command, cwd=str(job), check=True)
    except (OSError, subprocess.CalledProcessError) as error:
        self.print_log(f"MOOSE launch failed: {error}", "warning")
        raise
    self.print_log(f"MOOSE Complete. Time Required {time() - started} Seconds")
