import os
import sys
import subprocess

def parse_pflotran_vtk(inp_file, pflotran_output_file, jobname):

        print '--> Parsing PFLOTRAN output'
        header = ['# vtk DataFile Version 2.0\n',
                  'PFLOTRAN output\n',
                  'ASCII\n']
        fle = jobname + pflotran_output_file 
        inp_file = jobname + inp_file
        print fle 
        out_dir = 'parsed_vtk' 
        replacements = {'CELL_DATA':'POINT_DATA'} 
        before_first_point_line = True
        if os.stat(fle).st_size == 0:
            print 'ERROR: opening an empty vtk file to get the final vtk file'
            exit()
        
        temp_file = fle[:-4] + '_temp.vtk'
        with open(fle, 'r') as infile, open(temp_file, 'w') as outfile:
            print 'infile ', infile
            print 'outfile ', outfile
            ct = 0 
            for line in infile:
                print line
                if 'CELL_DATA' in line:
                    num_cells = line.strip(' ').split()[1]
                    outfile.write('POINT_DATA\t ' + num_cells + '\n')
                else: 
                    outfile.write(line)
        infile.close()
        outfile.close()
        vtk_filename = out_dir + '/' + fle.split('/')[-1]
        if not os.path.exists(os.path.dirname(vtk_filename)):
            os.makedirs(os.path.dirname(vtk_filename))
        arg_string = './inp2vtk' + ' '  +  inp_file + ' ' + vtk_filename  
        subprocess.call(arg_string, shell=True)
        arg_string = 'tail -n +5 ' + temp_file + ' > ' + temp_file + '.tmp && mv ' +  temp_file +  '.tmp ' + temp_file  
        print arg_string 
        subprocess.call(arg_string, shell=True)
        arg_string = 'cat ' +  temp_file + ' >> ' + vtk_filename
        subprocess.call(arg_string, shell=True) 
        print '--> Parsing PFLOTRAN output complete'

subprocess.call('rm /home/nknapp/dfnworks-main/inp_2_vtk/tests/dfn_explicit-000.vtk', shell=True)
subprocess.call('cp /home/jhyman/networks/single_fracture_3x3_uni/dfn_explicit-000.vtk /home/nknapp/dfnworks-main/inp_2_vtk/tests/', shell=True)
inp_file = sys.argv[1]
pflotran_output_file = sys.argv[2]
jobname = sys.argv[3]

parse_pflotran_vtk(inp_file, pflotran_output_file, jobname)
