import os

def edit_intersection_files(nPoly, keep_list):
    i = 6
	pull_list = list(set(range(1,nPoly+ 1)) - set(keep_list))
    filename = 'intersections_%d.inp'%i	
    print '--> Working on: ', filename
    lagrit_script = 'read / %s / mo1'%filename
    lagrit_script += '''
pset / pset2remove / attribute / b_a / 1,0,0 / eq / %d
'''%pull_list[0]	
    for j in pull_list[1:]:
        lagrit_script += '''
pset / prune / attribute / b_a / 1,0,0 / eq / %d
pset / pset2remove / union / pset2remove, prune
#rmpoint / pset, get, prune
pset / prune / delete
'''%j
    lagrit_script += '''
rmpoint / pset, get, pset2remove 
rmpoint / compress

cmo / modatt / mo_line_work / imt / ioflag / l
cmo / modatt / mo_line_work / itp / ioflag / l
cmo / modatt / mo_line_work / isn / ioflag / l
cmo / modatt / mo_line_work / icr / ioflag / l

cmo / status / brief
dump / intersections_%d_prune.inp / mo1
finish
'''%i
    
    file_name = 'prune_intersection.lgi'
    f = open(file_name, 'w')
    f.write(lagrit_script)
    f.flush()
    f.close()
    os.system(lagrit_path +  '< prune_intersection.lgi > out.txt')

nPoly = 20267
keep_list = [15745]  
edit_intersection_files(nPoly, keep_list)

 
