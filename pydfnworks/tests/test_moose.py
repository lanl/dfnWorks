"""Launcher tests use fake Conda and MPI executables; no solver is started."""
import importlib.util
import os
from pathlib import Path
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1] / 'pydfnworks'
spec = importlib.util.spec_from_file_location('moose_launcher', ROOT / 'dfnFlow/moose.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)


class MooseTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='moose test ', dir=Path(__file__).parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.job = self.root / 'job'
        self.job.mkdir()
        self.deck = self.root / 'input deck.in'
        self.deck.write_text('[Mesh]\n[]\n')
        self.exe = self.root / 'falcon-opt'
        self.exe.write_text('#!/bin/bash\nexit 0\n')
        self.exe.chmod(0o755)
        self.setup = self.root / 'conda.sh'
        self.setup.write_text('''conda() {
    [[ "$1" == activate && "$2" == falcon-moose ]] || return 12
    [[ -z "${LD_LIBRARY_PATH+x}" ]] || return 13
    [[ "$OPENBLAS_NUM_THREADS" == 1 && "$OMP_NUM_THREADS" == 1 ]] || return 14
    export PATH="$(dirname "${BASH_SOURCE[0]}"):$PATH"
}
''')
        self.mpi = self.root / 'mpiexec'
        self.mpi.write_text('#!/bin/bash\nprintf "%s\\n" "$@" > mpi_args\npwd > launch_cwd\n')
        self.mpi.chmod(0o755)
        self.dfn = SimpleNamespace(flow_solver='MOOSE', ncpu=96,
                                   dfnFlow_file=str(self.deck), jobname=str(self.job),
                                   print_log=lambda *args: None)

    def run_moose(self):
        launcher.moose(self.dfn, executable=self.exe, conda_sh=self.setup,
                       conda_env='falcon-moose')

    def test_launch_and_environment_isolation(self):
        with patch.dict(os.environ, {'LD_LIBRARY_PATH': '/fake', 'OMP_NUM_THREADS': '8'}):
            self.run_moose()
            self.assertEqual(os.environ['LD_LIBRARY_PATH'], '/fake')
            self.assertEqual(os.environ['OMP_NUM_THREADS'], '8')
        self.assertEqual((self.job / 'mpi_args').read_text().splitlines(),
                         ['-n', '96', str(self.exe), '-i', self.deck.name])
        self.assertEqual((self.job / 'launch_cwd').read_text().strip(), str(self.job))
        self.assertEqual((self.job / self.deck.name).read_text(), self.deck.read_text())
        self.dfn.dfnFlow_file = str(self.job / self.deck.name)
        self.run_moose()  # An input already in the job directory is valid.

    def test_solver_failure_propagates(self):
        self.mpi.write_text('#!/bin/bash\nexit 7\n')
        with self.assertRaises(subprocess.CalledProcessError) as caught:
            self.run_moose()
        self.assertEqual(caught.exception.returncode, 7)

    def test_activation_failure_stops_launch(self):
        self.setup.write_text('conda() { return 9; }\n')
        with self.assertRaises(subprocess.CalledProcessError):
            self.run_moose()
        self.assertFalse((self.job / 'mpi_args').exists())

    def test_invalid_configuration(self):
        self.dfn.flow_solver = 'PFLOTRAN'
        with self.assertRaises(ValueError):
            self.run_moose()
        self.dfn.flow_solver = 'MOOSE'
        self.dfn.ncpu = 0
        with self.assertRaises(ValueError):
            self.run_moose()

    def test_flow_dispatch_and_class_registration(self):
        # Load flow.py without requiring the full scientific Python stack.
        import sys
        from unittest.mock import Mock
        spec = importlib.util.spec_from_file_location('flow', ROOT / 'dfnFlow/flow.py')
        flow = importlib.util.module_from_spec(spec)
        with patch.dict(sys.modules, {'numpy': Mock()}):
            spec.loader.exec_module(flow)
        self.dfn.moose = Mock()
        self.dfn.dump_time = Mock()
        flow.set_flow_solver(self.dfn, 'MOOSE')
        flow.dfn_flow(self.dfn)
        self.dfn.moose.assert_called_once_with()
        import ast
        tree = ast.parse((ROOT / 'general/dfnworks.py').read_text())
        cls = next(node for node in tree.body if isinstance(node, ast.ClassDef)
                   and node.name == 'DFNWORKS')
        self.assertTrue(any(isinstance(node, ast.ImportFrom)
                            and node.module == 'pydfnworks.dfnFlow.moose'
                            and any(alias.name == 'moose' for alias in node.names)
                            for node in cls.body))


if __name__ == '__main__':
    unittest.main()
