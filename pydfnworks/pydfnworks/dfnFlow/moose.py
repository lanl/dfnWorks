# Alan connects to Moose. 
import os 

def moose(self):


    cmd = f" mpiexec -n {self.ncpu} {os.environ['MOOSE_EXE']} {self.local_dfn_flow_file}"

