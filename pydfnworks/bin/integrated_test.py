from integrated import *
from create_run_scripts import *

if __name__ == '__main__':

    domain=create_domain()
    domain['x_length']=100
    domain['y_length']=10
    domain['z_length']=10

    domain['x_increase']=0.5    
    domain['y_increase']=0.5    
    domain['z_increase']=0.5    

    domain['h']=0.01

    domain['inflow_boundary']='left_w'
    domain['outflow_boundary']='right_e'

    domain['visualization_mode']=False

    domain['inflow_pressure']=2.0*10**6
    domain['outflow_pressure']=1.0*10**6

    domain['stop_condition']['p32']=True

    domain['number_of_fractures']=7500
    domain['number_of_particles']=100
    domain['number_of_layers']=0


    domain['layer']=[]
    domain['layer'].append([-5,0])
    domain['layer'].append([0,5])

    domain['aperture']['constant']=True
    domain['aperture']['value']=10**-5

    domain['permeability']['cubic']=True

    fractures=[]

    f=fracture_family(1)
    f['probability']=0.33
    f['type']['rect']=True
    f['distribution']['constant']=True
    f['constant']['value']=0.5
    f['fisher']['theta']=0
    f['fisher']['phi']=0
    f['fisher']['kappa']=20
    f['min']=1
    f['max']=5
    f['p32']=1.75
    check_family_information(f)
    fractures.append(f)

    f=fracture_family(2)
    f['probability']=0.33
    f['type']['rect']=True
    f['distribution']['constant']=True
    f['constant']['value']=0.5
    f['fisher']['theta']=90
    f['fisher']['phi']=0
    f['fisher']['kappa']=20
    f['min']=1
    f['max']=5
    f['p32']=1.75
    check_family_information(f)
    fractures.append(f)

    f=fracture_family(3)
    f['probability']=0.34
    f['type']['rect']=True
    f['distribution']['tpl']=True
    f['tpl']['alpha']=2.5
    f['fisher']['theta']=90
    f['fisher']['phi']=90
    f['fisher']['kappa']=20
    f['min']=1
    f['max']=5
    f['p32']=1.75
    check_family_information(f)
    fractures.append(f)

    user_fractures_list=[]
    uf=user_fractures()
    uf['type']['rect_by_input']=False
    uf['path']='/home/jhyman/dfnworks/dfnworks-main/sample_inputs/4_fracture_test/4_user_rects.dat'
    user_fractures_list.append(uf)

    #create_dfnGen_input(domain, fractures, user_fractures_list)
    create_dfnGen_input(domain, fractures)
    create_pflotran_input(domain)
    create_dfntrans_input(domain)
