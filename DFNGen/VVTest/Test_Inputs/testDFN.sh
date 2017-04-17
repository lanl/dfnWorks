# Shell script running DFNGen V.V Tests
#
#
# In the python code which runs all the tests,
# DFNGen is called explicitly
# This script is then used to mesh the resulting
# output if needed

 
if [ $# -ne 3 ] ; then
	echo 'Not enough input arguments supplied'
	echo '1 - name of directory for outputs'
	echo '2 - input filename'
	echo '3 - number of CPUs used for meshing'
	exit 1
fi

 
  
# path settings for  Mathematica, PFLOTRAN, python, LAGRIT, and DFNWorks source code
#~~~~~~~~~~~~~~~~~~ 
 # For PETSC to be used for PFLOTRAN
#export PETSC_DIR=/home/satkarra/src/petsc-git/petsc
#export PETSC_ARCH=RHEL-6.5-nodebug
#export PETSC_ARCH=/home/satkarra/src/petsc-hg/linux-gnu-debug/


# mathematica source files path
export DFNGENC_PATH=/home/jharrod/GitProjects/DFNGen/DFNC++Version
export DFNGEN_PATH=/home/nataliia/DFNWorks_UBUNTU/DFNgenerator
#export DFNWORKS_PATH=/home/nataliia/DFNWorks_UBUNTU/
#export MATH_KERNEL=/n/local_linux/mathematica8.0/Executables/math
#export DFNFLOW_PATH=/home/nataliia/DFNWorks_UBUNTU/PFLOTRAN_pyscripts
#export DFNTRANS_PATH=/home/nataliia/DFNWorks_UBUNTU/ParticleTracking
#export PFLOTRAN_DIR=/home/satkarra/src/pflotran-dev-Ubuntu-14.04/
#export PFLOTRAN_DIR=/home/satkarra/src/pflotran-dev
export python_dfn=/n/local_linux/bin/python2.7
#export python_dfn=/scratch/er/dharp/source/epd-7.3-1-rh3-x86_64/bin/python
export lagrit_dfn=/n/swdev/LAGRIT/bin/lagrit_lin


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. DFNGen:C++ code for generating the DFN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo "Creating DFN"

${DFNGENC_PATH}/./main $2 $1

OUT=$?
if [ $OUT -eq 1 ]; then
   exit 1
fi

echo DFN Generation is Done!



if  [ -f $1/params.txt ] 
then 
	echo "Meshing..." 
else
	echo "Could not find params.txt"	
    exit 1
fi
	

cp ${DFNGENC_PATH}/new_mesh_DFN.py $1
cp ${DFNGEN_PATH}/dfn/user_function.lgi $1

#cp $2 $1/stat/mathInput.m


#  LaGriT: meshes DFN 

cd $1
# MESHING

$python_dfn new_mesh_DFN.py params.txt $3 

#cd ../

# if you would like to stop here
#exit 1

