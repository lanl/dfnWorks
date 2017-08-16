import pydfnworks 

if __name__ == '__main__':
    path = sys.argv[1]
    domain=create_domain()
    domain['x_length']=5
    domain['y_length']=5
    domain['z_length']=5

    domain['h']=0.1

    domain['inflow_boundary']='top'
    domain['outflow_boundary']='bottom'

    domain['inflow_pressure']=2.0*10**6
    domain['outflow_pressure']=1.5*10**6

    domain['stop_condition']['number']=True

    domain['number_of_fractures']=100
    domain['number_of_particles']=100
    domain['number_of_layers']=0
    

    domain['layer']=[]
    domain['layer'].append([-5,0])
    domain['layer'].append([0,5])


    domain['aperture']['constant']=True
    domain['aperture']['value']=10**-5

    domain['permeability']['cubic']=True
    domain['number_of_families'] = 3

    fractures=[]

    f=fracture_family(1)
    f['probability']=0.5
    f['type']['rect']=True
    f['distribution']['tpl']=True
    f['tpl']['alpha']=2.6
    f['fisher']['theta']=45
    f['fisher']['phi']=45
    f['fisher']['kappa']=20
    f['min']=2
    f['max']=6
    check_family_information(f)
    fractures.append(f)

    f=fracture_family(2)
    f['probability']=0.5
    f['type']['rect']=True
    f['distribution']['constant']=True
    f['constant']['value']=1
    f['fisher']['theta']=0
    f['fisher']['phi']=45
    f['fisher']['kappa']=20
    check_family_information(f)
    fractures.append(f)

    user_fractures_list=[]
    uf=user_fractures()
    uf['type']['rect_by_input']=True
    uf['path']='/home/jhyman/dfnworks/dfnworks-main/sample_inputs/4_fracture_test/4_user_rects.dat'
    user_fractures_list.append(uf)


    create_dfnGen_input(domain, path, fractures)
    print fractures
    create_pflotran_input(domain, path)
    create_dfntrans_input(domain, path)
    create_txt_input_file(path)
