from setuptools import setup
from setuptools.command.build_py import build_py
import subprocess
from multiprocessing import cpu_count


class BuildBinaries(build_py):
    def run(self, *args, **kwargs):
        subprocess.check_call(["make", "install", "-j", str(cpu_count())])
        return super().run(*args, **kwargs)


setup(cmdclass={"build_py": BuildBinaries})
