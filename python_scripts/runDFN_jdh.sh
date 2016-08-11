#!/bin/sh
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~ Three main parts of DFNWorks ~~~~~~~~~~~~~~~~~~~~~~~~~  
# 1. DFNGen:  Mathemtica script for fractures generation, python script for meshing
# using  LAGRIT, calls LaTeX for statistical report.
#
# 2. DFNFlow: first runs python scripts to prepare all the data for PFLOTRAN input,
# then runs PFLOTRAN
#
# 3. DFNTrans: runs DFNTrans C code executable for particle tracking.

# Note a), each of the parts have their own input  parameters control files, that shuld be 
# edited before running the current script.

# Note b), each of the parts can be performed independently. For example, once DFNGen generates a
# fracture network, the multiple flow solutions can be obtained for the same DFN 
# with different boundary condititions.
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

 if [ $# -ne 3 ] ; then
  echo 'Not enough input arguments supplied'
  echo '1 - name of directory for outputs'
  echo '2 - input filename'
  echo '3 - number of CPU used for meshing and flow solver'
 exit 1
 fi
 
  
# path settings for  Mathematica, PFLOTRAN, python, LAGRIT, and DFNWorks source code
#~~~~~~~~~~~~~~~~~~ 
 # For PETSC to be used for PFLOTRAN
export PETSC_DIR=/home/satkarra/src/petsc-git/petsc
export PETSC_ARCH=RHEL-6.5-nodebug
#export PETSC_ARCH=/home/satkarra/src/petsc-hg/linux-gnu-debug/


# mathematica source files path
export DFNGENC_PATH=/home/jhyman/dfnWorks/DFNGen/DFNC++Version
export DFNGEN_PATH=/home/nataliia/DFNWorks_UBUNTU/DFNgenerator
export DFNWORKS_PATH=/home/nataliia/DFNWorks_UBUNTU/
export MATH_KERNEL=/n/local_linux/mathematica8.0/Executables/math
export DFNFLOW_PATH=/home/nataliia/DFNWorks_UBUNTU/PFLOTRAN_pyscripts
export DFNTRANS_PATH=/home/nataliia/DFNWorks_UBUNTU/ParticleTracking
export PFLOTRAN_DIR=/home/satkarra/src/pflotran-dev-Ubuntu-14.04/
#export PFLOTRAN_DIR=/home/satkarra/src/pflotran-dev


export python_dfn=/n/local_linux/bin/python2.7
export lagrit_dfn=/n/swdev/LAGRIT/bin/lagrit_lin



#~~~~~~~~~~~~~~~~~~~~~~~~~~~~  
echo "Running job"
echo $1
 
echo "Creating output directories"
# create a directory for the DFNWorks output as specified by the first positional parameter
if [ -d $1 ] ; then 
	rm -f -r $1/*
else 
	mkdir -p $1
fi

cp $2 $1 # copy the input file into the specified output directory
# inside the output directory - create a sub-directory "stat" (where the statistics files will be stored) 
if [ -d $1/stat ] ; then 
	rm -r -f $1/stat/*
else 
	mkdir $1/stat
fi


date # print date on terminal

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 1. DFNGen:C++ code for generating the DFN
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo "Creating DFN"

${DFNGENC_PATH}/./main $2 $1 #| tee $1/programOutput.txt

OUT=$?
if [ $OUT -eq 1 ]; then
   exit 1
fi

echo DFN Generation is Done!

if  [ -f $1/params.txt ] 
then 
	echo "Meshing proceeds" 
else
        exit 1
fi
	

# copy DFNGen input, Python code, Matlab code
cp $2 $1

#cp ${DFNGENC_PATH}/new_mesh_DFN.py $1
cp /home/jhyman/dfnWorks/dfnworks-main/python_scripts/mesh_DFN_C++_v2.py $1

#cp $2 $1/stat/mathInput.m


#  LaGriT: meshes DFN 

cd $1
# MESHING
#$python_dfn new_mesh_DFN.py params.txt $3 
$python_dfn mesh_DFN_C++_v2.py params.txt $3  
#$python_dfn /home/jhyman/Code/python/convert_avs_to_vtk.py full_mesh.inp full_mesh binary

# PDFLatex: creates report file of DFN statistics
#mv finalmesh.txt stat/
#cd stat

 
#pdflatex stat.tex > log_pdflatex
#mv stat.pdf .. 
#rm -f stat.aux stat.log mathInput.m

#echo "Statistical summary of generated DFN is in stat.pdf file." 
#echo
#echo

# if you would like to stop here
# exit 1
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 2. DFNFlow: Flow solution
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "~~~~ Program: DFNWorks / DFNFlow lead by PFLOTRAN ~~~~~~~~"
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~"
echo "~~~ Following python scripts will run to prepare ~~~~~~~~~"
echo "~~~~~~ input data for PFLOTRAN running ~~~~~~~~~~~~~~~~~~~"
echo "~~ Developers: Satish Karra, Nataliia Makedonska ~~~~~~~~~"
echo "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~" 
ln -s /home/jhyman/dfnWorks/pflotran_driver_debug/driver.py .
ln -s /home/jhyman/dfnWorks/pflotran_driver_debug/dfnworks_v3.py .
ln -s /home/jhyman/dfnWorks/pflotran_driver_debug/dfntools.py .
ln -s /scratch/nobackup/jhyman/2016-mixing/python_scripts/uncorrelated.py ./

cp perm.dat perm_save.dat
cp aperture.dat aperture_save.dat

ln -s ${DFNFLOW_PATH}/postprocess.py

$python_dfn uncorrelated.py 0 
$python_dfn driver.py

#rm -rf materialid.dat lagritrun*.txt full_mesh.uge materialid.inp

#run PFLOTRAN
cp /scratch/nobackup/jhyman/2016-mixing/dfn_explicit.in ./
echo "Make sure you use proper input file for PFLOTRAN!!!"
${PETSC_DIR}/${PETSC_ARCH}/bin/mpirun -np $3 $PFLOTRAN_DIR/src/pflotran/pflotran -pflotranin dfn_explicit.in

$python_dfn postprocess.py

cat dfn_explicit-cellinfo-001-rank*.dat > cellinfo.dat  
cat dfn_explicit-darcyvel-001-rank*.dat > darcyvel.dat  

rm -f dfn_explicit-cellinfo*.dat dfn_explicit-darcyvel*.dat
###if you would like to stop here
exit 1


# create uge file
ln -s ${DFNFLOW_PATH}/driver.py 



# create *.ex files for boundaries (not necessary to run for all the boundaries of the domain,

$python_dfn driver.py


rm -rf materialid.dat lagritrun*.txt

#run PFLOTRAN
#

#echo $DFNWORKS_PATH
cp ${DFNWORKS_PATH}/test_4fractures/dfn_explicit.in .
echo "Make sure you use proper input file for PFLOTRAN!!!"
#mpirun -np $3 $PFLOTRAN_DIR/src/pflotran/pflotran -pflotranin dfn_explicit.in
${PETSC_DIR}/${PETSC_ARCH}/bin/mpirun -np $3 $PFLOTRAN_DIR/src/pflotran/pflotran -pflotranin dfn_explicit.in

cat dfn_explicit-cellinfo-001-rank*.dat > cellinfo.dat  
cat dfn_explicit-darcyvel-001-rank*.dat > darcyvel.dat  

rm -f dfn_explicit-cellinfo*.dat dfn_explicit-darcyvel*.dat

# if you would like to stop here
# exit 1

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# 5. Running Particle Tracking code 
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# create a link to executable

ln -s ${DFNTRANS_PATH}/DFNTrans

# copy the control file for Particle Tracking
echo "Make sure you use proper input file for Transport!!!"
cp ${DFNWORKS_PATH}/test_4fractures/PTDFN_control.dat .

./DFNTrans 

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
echo "Job complete"
echo $1
date # print out the time again
