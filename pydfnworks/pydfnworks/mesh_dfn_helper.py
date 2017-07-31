"""
.. module:: mesh_dfn_helper.py
   :synopsis: helper functions for meshing dfn using lagrit  
.. moduleauthor:: Jeffrey Hyman <jhyman@lanl.gov>

"""

import glob
from os import remove

def parse_params_file():
    """ Reads params.txt file and parse information
    
    Returns:
        * num_poly: (int) Number of Polygons
        * h: (float) meshing length scale h
        * dudded_points: (int) Expected number of dudded points in Filter (LaGriT)
        * visual_mode: True/False
        * domain: dict: x,y,z domain sizes 
    """
    print("\n--> Parsing  params.txt")
    fparams = open('params.txt', 'r')
    # Line 1 is the number of polygons
    num_poly=int(fparams.readline())
    #Line 2 is the h scale
    h=float(fparams.readline())
    # Line 3 is the visualization mode: '1' is True, '0' is False.
    visual_mode = int(fparams.readline())
    # line 4 dudded points
    dudded_points = int(fparams.readline())

    # Dict domain contains the length of the domain in x,y, and z    
    domain = {'x': 0, 'y': 0, 'z': 0}
    #Line 5 is the x domain length
    domain['x']=(float(fparams.readline()))
    
    #Line 5 is the x domain length 
    domain['y']=(float(fparams.readline()))

    #Line 5 is the x domain length 
    domain['z']=(float(fparams.readline()))
    fparams.close()
    
    print("Number of Polygons: %d"%num_poly)
    print("H_SCALE %f"%h)
    if visual_mode > 0:
        visual_mode = True 
        print("Visual mode is on")
    else:
        visual_mode = False
        print("Visual mode is off")
    print("Expected Number of duded points: %d"%dudded_points)
    print("X Domain Size %d m"%domain['x'])
    print("Y Domain Size %d m"%domain['y'])
    print("Z Domain Size %d m"%domain['z'])
    print("--> Parsing params.txt complete\n")
    return(num_poly, h, visual_mode, dudded_points, domain)
    
def check_dudded_points(dudded):
    """Parses Lagrit log_merge_all.txt and checks if number of dudded points
    is the expected number
    Returns: A
        * True if the number of dudded points is correct 
        * False if the number of dudded points is incorrect 
    """
    print "Checking that number of Dudded points is correct"
    datafile = file('log_merge_all.txt')
    for line in datafile:
        if 'Dudding' in line:
            print 'From LaGriT: '
            print line
            break
    try:
        pts = int(line.split()[1])
    except:
        pts = int(line.split()[-1])
    print("Expected Number of points: %d"%dudded)
    print("Actual Number of points: %d"%pts)
    diff = abs(dudded - pts)
    if diff == 0:
        print '--> Correct Number of points removed \n'
        return True
    elif diff < 5: 
        print('--> WARNING!!! Number of points removed does not \
            match expected value')
        print("However value is small: %d"%diff)
        print("Proceeding\n")
        return True
    else:
        print 'ERROR! Incorrect Number of points removed'
        print 'Expected Number ', dudded
        return False
    

def cleanup_dir():
    """ Removes files from meshing """

    files_to_remove=['part*', 'log_merge*', 'merge*', 'mesh_poly_CPU*',
                    'mesh*inp', 'mesh*lg']
    for name in files_to_remove:
        for fl in glob.glob(name):
            remove(fl)    

def output_meshing_report(visual_mode):
    """ Prints information about the final mesh to file"""

    f = open('finalmesh.txt','w')
    f.write('The final mesh of DFN consists of: \n')
    if not visual_mode: 
        print "Output files for flow calculations are written in :"
        print "--> full_mesh.gmv"
        print "--> full_mesh.inp"
        print "--> full_mesh.lg"
        print "--> full_mesh.uge"
        print "--> tri_fracture.stor"

        finp=open('full_mesh.inp','r')
        g = finp.readline()
        g = g.split()
        NumElems = int(g.pop(1))
        NumIntNodes = int(g.pop(0))
        f.write(str(NumElems)+' triangular elements; \n')
        f.write(str(NumIntNodes)+'  nodes / control volume cells; \n')
        finp.close()
        
        fstor=open('tri_fracture.stor','r')
        fstor.readline()
        fstor.readline()
        gs = fstor.readline()
        gs = gs.split()
        NumCoeff = int(gs.pop(0))
        f.write(str(NumCoeff)+' geometrical coefficients / control volume faces. \n')
        fstor.close()
    else:
        print "Output files for visualization are written in :"
        print "--> reduced_mesh.gmv"
        print "--> reduced_mesh.inp"
        finp=open('reduced_mesh.inp','r')
        g = finp.readline()
        g = g.split()
        NumElems = int(g.pop(1))
        NumIntNodes = int(g.pop(0))
        f.write(str(NumElems)+' triangular elements; \n')
        f.write(str(NumIntNodes)+'  nodes / control volume cells. \n')
        finp.close()
    f.close()



