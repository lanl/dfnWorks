import argparse
from dfnworks import dfnworks
 
def commandline_options():
    """Read command lines for use in dfnWorks.

    Parameters
    ----------
        None
    
    Returns
    ---------
        options : argparse function
            command line options 
   
    Notes
    ---------
        Options:
            -name : string
                Path to working directory (Mandatory) 
            -ncpu : int 
                Number of CPUS (Optional, default=4)
            -input : string 
                Input file with paths to run files (Mandatory if the next three options are not specified)
            -gen : string 
                Generator Input File (Mandatory, can be included within the input file)
            -flow : string 
                PFLORAN Input File (Mandatory, can be included within the input file)
            -trans : string
                Transport Input File (Mandatory, can be included within the input file)
            -prune_file : string
                Absolute path to the prune Input File 
            -path : string
                Path to another DFN run that you want to base the current run from 
            -cell : bool
                True/False Set True for use with cell based aperture and permeabuility (Optional, default=False)
    """
    parser = argparse.ArgumentParser(description="Command Line Arguments for dfnWorks")
    parser.add_argument("-name", "--jobname", default="", type=str,
              help="jobname") 
    parser.add_argument("-ncpu", "--ncpu", default=4, type=int, 
              help="Number of CPUs")
    parser.add_argument("-input", "--input_file", default="", type=str,
              help="input file with paths to run files") 
    parser.add_argument("-gen", "--dfnGen", default="", type=str,
              help="Path to dfnGen run file") 
    parser.add_argument("-flow", "--dfnFlow", default="", type=str,
              help="Path to dfnFlow run file") 
    parser.add_argument("-trans", "--dfnTrans", default="", type=str,
              help="Path to dfnTrans run file") 
    parser.add_argument("-path", "--path", default="", type=str,
              help="Path to directory for sub-network runs") 
    parser.add_argument("-cell", "--cell", default=False, action="store_true",
              help="Binary For Cell Based Apereture / Perm")
    parser.add_argument("-prune_file", "--prune_file", default="", type=str, 
              help="Path to prune DFN list file") 
    parser.add_argument("-prune_path", "--prune_path", default="", type=str, 
              help="Path to original DFN files") 
    options = parser.parse_args()
    if options.jobname is "":
        sys.exit("Error: Jobname is required. Exiting.")
    return options

def create_dfn():
    '''Parse command line inputs and input files to create and populate dfnworks class

    Parameters
    ----------
        None
 
    Returns
    -------
        DFN : object 
            DFN class object populated with information parsed from the command line. Information about DFN class is in dfnworks.py

    Notes
    -----
    None
    '''
    
    options = commandline_options()
    print("Command Line Inputs:")
    print options
    print("\n-->Creating DFN class")
    DFN=dfnworks(jobname=options.jobname, ncpu=options.ncpu)

    if options.input_file != "":
        with open(options.input_file) as f:
            for line in f:
                line=line.rstrip('\n')
                line=line.split()

                if line[0].find("dfnGen") == 0:
                    DFN.dfnGen_file = line[1]
                    DFN.local_dfnGen_file = line[1].split('/')[-1]

                elif line[0].find("dfnFlow") == 0:
                    DFN.dfnFlow_file = line[1]
                    DFN.local_dfnFlow_file = line[1].split('/')[-1]

                elif line[0].find("dfnTrans") == 0:
                    DFN.dfnTrans_file = line[1]
                    DFN.local_dfnTrans_file = line[1].split('/')[-1]
    else:   
        if options.dfnGen != "":
            DFN.dfnGen_file = options.dfnGen
            DFN.local_dfnGen_file = options.dfnGen.split('/')[-1]
        elif dfnGen_file != "":
            DFN.dfnGen_file = dfnGen_file  
            DFN.local_dfnGen_file = dfnGen_file.split('/')[-1]
        else:
            sys.exit("ERROR: Input File for dfnGen not provided. Exiting")
        
        if options.dfnFlow != "":
            DFN.dfnFlow_file = options.dfnFlow
            DFN.local_dfnFlow_file = options.dfnFlow.split('/')[-1]
        elif dfnFlow_file != "":
            DFN.dfnFlow_file = dfnFlow_file  
            DFN.local_dfnFlow_file = dfnFlow_file.split('/')[-1]
        else:
            sys.exit("ERROR: Input File for dfnFlow not provided. Exiting")
        
        if options.dfnTrans != "":
            DFN.dfnTrans_file = options.dfnTrans
            DFN.local_dfnTrans_file = options.dfnTrans.split('/')[-1]
        elif dfnTrans_file != "":
            DFN.dfnTrans_file = dfnTrans_file  
            DFN.local_dfnTrans_file = dfnTrans_file.split('/')[-1]
        else:
            sys.exit("ERROR: Input File for dfnTrans not provided. Exiting")

    if options.path != "":
        if not options.path.endswith('/'):
            options.path += os.sep
        DFN.path = options.path 
    else:
        DFN.path = ""

    if options.prune_file != "":
        DFN.prune_file = options.prune_file
    else:
        DFN.prune_file = ""

    if options.cell is True:
        DFN.aper_cell_file = 'aper_node.dat'
        DFN.perm_cell_file = 'perm_node.dat'
    else:
        DFN.aper_file = 'aperture.dat'
        DFN.perm_file = 'perm.dat'

    print("\n-->Creating DFN class: Complete")
    print 'Jobname: ', DFN.jobname
    print 'Number of cpus requested: ', DFN.ncpu 
    print '--> dfnGen input file: ',DFN.dfnGen_file
    print '--> dfnFlow input file: ',DFN.dfnFlow_file
    print '--> dfnTrans input file: ',DFN.dfnTrans_file

    print '--> Local dfnGen input file: ',DFN.local_dfnGen_file
    print '--> Local dfnFlow input file: ',DFN.local_dfnFlow_file
    print '--> Local dfnTrans input file: ',DFN.local_dfnTrans_file

    if options.cell is True:
        print '--> Expecting Cell Based Aperture and Permeability'

    print("="*80+"\n")  
    return DFN

