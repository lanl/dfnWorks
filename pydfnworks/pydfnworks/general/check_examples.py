import glob
import os
import subprocess
import sys
import numpy as np
from images import success, failure 
import shutil 
from rich.console import Console 

def check_4_user_rects(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")

        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))

        subprocess.call(cmd,shell=True)
        TotalNumberP = np.genfromtxt("/dfnWorks/work/4_user_rects_example/traj/TotalNumberP").astype(int)
        if TotalNumberP == 10:
            console.print("Correct number of particles exited the domain.",style="bold green")
            console.print("{0} Completed successfully!\n".format(name),style="bold green")
            flag = True
        else:
            console.print("{0} failed due to incorrect number of particles exiting the domain!".format(name),style="bold red")
            console.print("{0} particles exiting the domain. Expected 10".format(TotalNumberP),style="bold red")
            flag = False 
        os.chdir(cwd)
    except:
        print("{0} failed".format(name),style="bold red")
        os.chdir(cwd)
        pass
    return flag 

def check_user_ell_uniform(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")

        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))

        subprocess.call(cmd,shell=True)
        with open("/dfnWorks/work/4_user_ell_uniform_example/full_mesh.inp") as fp:
            line = fp.readline()
            num_points = int(line.split()[0])
        if num_points == 10021:
            print("Correct number of points in the mesh.")
            print("{0} Completed successfully!\n".format(name))
            flag = True
        else:
            print("{0} failed due to incorrect number of points in mesh!".format(name))
            flag = False 
        os.chdir(cwd)
    except:
         print("{0} Failed!".format(name))
         os.chdir(cwd)
         pass
    return flag 

def check_octree(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")
        
        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))
        
        subprocess.call(cmd,shell=True)
        with open("/dfnWorks/work/octree_example/octree/octree_dfn.inp") as fp:
            line = fp.readline()
            num_points = int(line.split()[0])
        if num_points == 26726:
            print("Correct number of points in the mesh.")
            print("{0} Completed successfully!\n".format(name))
            flag = True
        else:
            print("{0} failed due to incorrect number of points in mesh!".format(name))
            flag = False 
        os.chdir(cwd)
    except:
         print("{0} Failed!".format(name))
         os.chdir(cwd)
         pass
    return flag 

def check_ade(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")
        
        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))
        
        subprocess.call(cmd,shell=True)
        with open("/dfnWorks/work/ade_example/dfn_restart-mas.dat") as fp:
            fp.readline()
            line = fp.readline()
            tmp_tracer = float(line.split()[4])
            tracer = float(f"{tmp_tracer:.5f}")
        if tracer == 0.00074:
            print("Correct amount of tracer in system.")
            print("{0} Completed successfully!\n".format(name))
            flag = True
        else:
            print("{0} failed due to incorrect amount of tracer in system!".format(name))
            flag = False 
        os.chdir(cwd)
    except:
         print("{0} Failed!".format(name))
         os.chdir(cwd)
         pass
    return flag 

def check_tdrw(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")
        
        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))
        
        subprocess.call(cmd,shell=True)
        TotalNumberP = np.genfromtxt("/dfnWorks/work/{0}_example/traj/TotalNumberP".format(name)).astype(int)
        if TotalNumberP == 9989:
            print("Correct number of particles exited the domain.")
            print("{0} Completed successfully!\n".format(name))
            flag = True
        else:
            print("{0} Failed due to incorrect number of particles exiting the domain!".format(name))
            flag = False 
        os.chdir(cwd)
    except:
        print("{0} failed!".format(name))
        os.chdir(cwd)
        pass
    return flag 

def check_graph_transport(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")
        
        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))
        
        subprocess.call(cmd,shell=True)
        data = np.genfromtxt("/dfnWorks/work/{0}_example/graph_partime.dat".format(name),skip_header=1)
        n,m = np.shape(data)
        if n == 10000 and m == 4:
            print("Correct number of particles exited the domain.")
            print("{0} Completed successfully!\n".format(name))
            flag = True
        else:
            print("{0} Failed due to incorrect number of particles exiting the domain!".format(name))
            flag = False 
        os.chdir(cwd)
    except:
        print("{0} failed!".format(name))
        os.chdir(cwd)
        pass
    return flag 

def check_TPL(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")
        
        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))
        
        subprocess.call(cmd,shell=True)
        TotalNumberP = np.genfromtxt("/dfnWorks/work/{0}_example/traj/TotalNumberP".format(name)).astype(int)
        if TotalNumberP == 9983: 
            print("Correct number of particles exited the domain.")
            print("{0} Completed successfully!\n".format(name))
            flag = True
        else:
            print("{0} Failed due to incorrect number of particles exiting the domain!".format(name))
            flag = False 
        os.chdir(cwd)
    except:
        print("{0} failed!".format(name))
        os.chdir(cwd)
        pass
    return flag 

def check_in_fracture_var(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")
        
        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))
        
        subprocess.call(cmd,shell=True)
        traj_length = np.genfromtxt("/dfnWorks/work/{0}_example/traj/partime".format(name),skip_header=1)[:,-1]
        mu = np.mean(traj_length)
        if int(mu*100) == 135:
            print("Correct Tortuosity.")
            print("{0} Completed successfully!\n".format(name))
            flag = True
        else:
            print("{0} Failed due to incorrect Tortuosity".format(name))
            flag = False 
        os.chdir(cwd)
    except:
        print("{0} failed!".format(name))
        os.chdir(cwd)
        pass
    return flag 


def check_pruning(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")
        
        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))
        
        subprocess.call(cmd,shell=True)
        TotalNumberP = np.genfromtxt("/dfnWorks/work/{0}_example/2_core/traj/TotalNumberP".format(name)).astype(int)
        if TotalNumberP == 10238: 
            print("Correct number of particles exited the domain.")
            print("{0} Completed successfully!\n".format(name))
            flag = True
        else:
            print("{0} Failed due to incorrect number of particles exiting the domain!".format(name))
            flag = False 
        os.chdir(cwd)
    except:
        print("{0} failed!".format(name))
        os.chdir(cwd)
        pass
    return flag 

def check_reservoir(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")
        
        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))
        
        subprocess.call(cmd,shell=True)
        pflotran_output_file = "/dfnWorks/work/{0}_example/ResModPFLOTRAN.out".format(name)
        print("\n--> Opening %s to check for convergence" %
        pflotran_output_file)
        with open(pflotran_output_file, "r") as fp:
            for line in fp.readlines():
                if "STEADY-SOLVE      1 snes_conv_reason:" in line:
                    print("--> PFLOTRAN converged")
                    print("{0} Completed successfully!\n".format(name))
                    flag = True
                    os.chdir(cwd)
                    return flag 
        if not flag:
            print("{0} Failed Due to PFLOTRAN Convergence".format(name))
            os.chdir(cwd)
    except:
        print("{0} failed!".format(name))
        os.chdir(cwd)
        pass
    return flag 


def check_fehm(name):
    flag = False
    cwd = os.getcwd()
    try:
        os.chdir(name)
        cmd = "bash notes.txt > ../check_example_logs/{0}_check.log".format(name)
        console.print("Running: --> {0}".format(cmd),style="blue")
        
        if os.path.isdir("/dfnWorks/work/{0}_example".format(name)):
            shutil.rmtree("/dfnWorks/work/{0}_example".format(name))
        
        subprocess.call(cmd,shell=True)
        fehm_output_file = "/dfnWorks/work/{0}_example/tri_frac.out".format(name)
        print("\n--> Opening %s to check for convergence" %
        fehm_output_file)
        with open(fehm_output_file, "r") as fp:
            for line in fp.readlines():
                if "simulation ended:" in line:
                    print("--> FEHM Simulation Completed")
                    print("{0} Completed successfully!\n".format(name))
                    flag = True
        if not flag:
            print("{0} Failed".format(name))
            os.chdir(cwd)
    except:
        print("{0} failed!".format(name))
        os.chdir(cwd)
        pass
    return flag 


def check_example(name):

    if name == "4_user_rects":
        return check_4_user_rects(name)
    elif name == "4_user_ell_uniform":
        return check_user_ell_uniform(name)
    elif name == "ade":
        return check_ade(name)
    elif name == "octree":
        return check_octree(name)
    elif name == "tdrw":
        return check_tdrw(name)
    elif name == "graph_transport":
        return check_graph_transport(name)
    elif name == "TPL":
        return check_TPL(name)
    elif name == "in_fracture_var":
        return check_in_fracture_var(name)
    elif name == "pruning":
        return check_pruning(name)
    elif name == "reservoir":
        return check_reservoir(name)
    elif name == "fehm":
        return check_fehm(name)
    else:
        print("Unknown example {0}".format(name))
        return False

def gather_all_examples():
    example_list = ["4_user_rects","4_user_ell_uniform",
                    "octree","ade","tdrw","graph_transport",
                    "TPL","in_fracture_var","pruning",
                    "reservoir","fehm"] 

    return example_list

if __name__ == '__main__':

    if len(sys.argv) > 1:
        example_name = sys.argv[1]
        example_list = [example_name]
    else:
        example_list = gather_all_examples()

    try:
        os.mkdir("check_example_logs")
    except:
        shutil.rmtree("check_example_logs")
        os.mkdir("check_example_logs")

    console = Console()
    pass_list = []
    fail_list = []
    for example_name in example_list:
        console.print("\nChecking Example: {0}".format(example_name), style="bold blue")
        if check_example(example_name):
            console.print("Example {0} passed\n".format(example_name),style="bold green")
            pass_list.append(example_name)
        else: 
            console.print("Example {0} failed\n".format(example_name),style="bold red")
            fail_list.append(example_name)

    console.print("Examples Complete\n",style="blue")
    console.print("Successful tests:",style="green")
    print(pass_list)

    console.print("Failed tests:",style="red")
    print(fail_list)

    if len(fail_list) == 0:
        console.print(success(),style="red")
    else:
        console.print(failure(),style="bold yellow")
