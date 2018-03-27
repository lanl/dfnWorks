import sys

def create_domain():
    ''' Create Dictionary for domain variables'''
    domain={}
    domain['x_length']=float()
    domain['y_length']=float()
    domain['z_length']=float()

    domain['x_increase']=float()    
    domain['y_increase']=float()    
    domain['z_increase']=float()    

    domain['inflow_boundary']=[]    
    domain['outflow_boundary']=[]    

    domain['inflow_pressure']=2.0*10**6
    domain['outflow_pressure']=10**6

    domain['angle']={'radians':True, 'degrees':False}
 
    domain['radiiListIncrease']=0.1
    
    domain['h']=float()

    domain['number_of_fractures']=int()
    domain['number_of_families']=int() 

    domain['stop_condition']={'p32':False,'number':False}
    domain['fram_off']=False
    domain['output_all_radii']=True  
    domain['number_of_layers']=0

    domain['triple_intersections']=False

    domain['output_accepted_radii_per_family']=True
    domain['output_final_radii_per_family']=True
    domain['insert_user_rectangles_first']=True
    domain['force_large_fractures']=False
    domain['remove_fractures_less_than']=float()

    domain['multiple_clusters']=False
    domain['print_rejection_reasons']=False            
    domain['visualization_mode']=False

    domain['keep_only_largest_cluster']=True
    domain['ignore_boundary_faces']=False  
    domain['seed']= 92731535

    domain['rejects_per_fracture']=10
    domain['radii_list_increase']=0.1

    domain['aperture']={'log_normal':False, 'log_mean': float(), 'std': float(), 
            'from_trans': False, 'F_T':float(), 'B_T': float(), 
            'constant': False, 'value':float(), 
            'from_size': False, 'F_r':float(), 'B_r':float()}
    domain['permeability']={'cubic':False, 'constant': False, 'value': float()}
    return domain

def fracture_family(family_number):
    '''Create Fracture family dictionary'''
    family={}
    family['number']=family_number
    family['probability']={}
    family['type']={'rect':False, 'ellipse':False}
    family['layer']=0
    family['p32']=0.0
    family['aspect']=1.0
    family['number_of_points']=int()
    family['beta_distribution']=True
    family['beta']=0
    # fisher distribution
    family['fisher']={'theta':float(), 'phi':float(), 'kappa':float()}
    family['distribution']={ 'tpl':False , 'log_normal':False, 'exp': False, 'constant':False}
    family['tpl']={'alpha':-1}
    family['log_normal']={'mean':-1, 'std':-1}
    family['exp']={'mean':-1}
    family['constant']={'value':-1}
    family['min']=-1
    family['max']=-1
    return family

def user_fractures():
    ''' Create User fracture dictionary'''
    uf={} 
    uf['type']={'rect_by_coord':False, 'ell_by_coord':False, 'rect_by_input':False, 'ell_by_input':False}
    uf['path']=[]
    return uf 
 
def check_family_information(f):
    '''Check for consistancy within fracture family f''' 
    print("\nFamily Number: %d"%f['number']) 
    if f['type']['rect']: 
        print("Family Type : rectangles")
        f['number_of_points']=4
    elif f['type']['ellipse']:
        print("Family Type : ellipses")
        if f['number_of_points'] > 0:
            print("Number of points: %d"%f['number_of_points'])
        else:
            sys.exit("ERROR: Number of points not specified") 
    else:
        sys.exit("ERROR: Family Type not specified") 
    if f['probability'] > 0:
        print("Family Probability: %0.2f"%f['probability'])
    else:
       sys.exit("ERROR: Family Probability not specified") 
    if f['layer']>0:
        print("Family Layer: %d"%f['layer'])
    else:
        print("Sampling Fracture Centers from whole domain")
    if f['p32'] > 0:
        print("P_32: %0.2e"%f['p32'])
    print("Aspect ratio: %d"%f['aspect'])
   
    print("Fisher Distribution Parameters")
    if f['fisher']['theta'] >= 0:
        print("--> Theta: %0.2f"%f['fisher']['theta'])
    else:
        sys.exit("ERROR: Theta not specified") 
    if f['fisher']['phi'] >= 0:
        print("--> Phi: %0.2f"%f['fisher']['phi'])
    else:
        sys.exit("ERROR: Phi not specified") 
    if f['fisher']['kappa'] >= 0:
        print("--> kappa: %0.2f"%f['fisher']['kappa'])
    else:
       sys.exit("ERROR: Kappa not specified") 
       
 
    if f['distribution']['tpl']:
        print("Sampling Fracture radii from Truncated Power Law Distribution")
        if f['tpl']['alpha'] > 0:
            print("--> Alpha: %0.2f"%f['tpl']['alpha'])
        else:   
            sys.exit("ERROR: Alpha not specified") 
    elif f['distribution']['log_normal']:
        print("Sampling Fracture radii from Log Normal Distribution")
        if f['log_normal']['mean'] > 0:
            print("--> Mean: %0.2f"%f['log_normal']['mean'])
        else:   
            sys.exit("ERROR: Mean not specified") 
        if f['log_normal']['std'] > 0:
            print("--> STD: %0.2f"%f['log_normal']['std'])
        else:   
            sys.exit("ERROR: STD not specified") 
    elif f['distribution']['exp']:
        print("Sampling Fracture radii from Exponential Distribution")
        if f['exp']['mean'] > 0:
            print("--> Mean: %0.2f"%f['exp']['mean'])
        else:   
            sys.exit("ERROR: Mean not specified") 
    elif f['distribution']['constant']:
        print("Fracture radii are constant")
        if f['constant']['value'] > 0:
            print("--> Mean: %0.2f"%f['constant']['value'])
            f['min']=f['constant']['value']
            f['max']=f['constant']['value']
        else:   
            sys.exit("ERROR: Constant value not specified") 
    else:
        sys.exit("ERROR: Distribution not specified")
    # check min/max fracture radius 
    if f['min'] > 0:
        print("--> Minimum fracture radius: %0.2f"%f['min'])
    else:
        sys.exit("ERROR: Minimum fracture radius not specified") 
    if f['max'] > 0:
        print("--> Maximum fracture radius: %0.2f"%f['max'])
    else:
        sys.exit("ERROR: Minimum fracture radius not specified") 
    print ''

def check_domain_information():
    '''Check for consistancy within domain dictionary'''
    boundary_list=['top', 'bottom', 'left_w', 'front_n', 'right_e', 'back_s']
    if domain['inflow_boundary'] in boundary_list:
        print("Inflow boundary is %s"%domain['inflow_boundary'])
    else:
        sys.exit("ERROR: Inflow Boundary not specified") 
    if domain['outflow_boundary'] in boundary_list:
        print("Outflow boundary is %s"%domain['outflow_boundary'])
    else:
        sys.exit("ERROR: Outflow Boundary not specified") 

def family():
    '''Create dictionary for grouping parameters'''
    obj = {'probability':[], 'layer':[], 'p32':[], 'aspect':[],
        'number_of_points':[], 'beta':[], 'theta':[], 'phi':[], 'kappa':[],
        'dist':[],'log_min':[], 'log_max':[], 'log_mean':[], 'sd':[],
        'exp_max':[], 'exp_min':[], 'exp_mean':[], 
        'min':[], 'max':[], 'alpha':[],
        'constant':[], 'betaDistribution':[]}  
    return obj

def group_family(fractures, number_of_families, shape):
    '''Group generation parameters by family''' 
    obj=family()
    for i in range(number_of_families):
        if fractures[i]['type'][shape]: 
            obj['probability'].append(fractures[i]['probability'])
            obj['layer'].append(fractures[i]['layer'])
            obj['p32'].append(fractures[i]['p32'])
            obj['beta'].append(int(fractures[i]['beta']))
            obj['betaDistribution'].append(int(fractures[i]['beta_distribution']))
            obj['aspect'].append(fractures[i]['aspect'])
            obj['number_of_points'].append(fractures[i]['number_of_points'])
            obj['theta'].append(fractures[i]['fisher']['theta'])
            obj['phi'].append(fractures[i]['fisher']['phi'])
            obj['kappa'].append(fractures[i]['fisher']['kappa'])

            if fractures[i]['distribution']['log_normal']:
                obj['dist'].append(1)
                obj['log_min'].append(fractures[i]['min'])
                obj['log_max'].append(fractures[i]['max'])
                obj['sd'].append(fractures[i]['log_normal']['std'])
                obj['log_mean'].append(fractures[i]['log_normal']['mean'])

            elif fractures[i]['distribution']['tpl']:
                obj['dist'].append(2)
                obj['min'].append(fractures[i]['min'])
                obj['max'].append(fractures[i]['max'])
                obj['alpha'].append(fractures[i]['tpl']['alpha'])

            elif fractures[i]['distribution']['exp']:
                obj['dist'].append(3)
                obj['exp_min'].append(fractures[i]['min'])
                obj['exp_max'].append(fractures[i]['max'])
                obj['exp_mean'].append(fractures[i]['exp']['mean'])

            elif fractures[i]['distribution']['constant']:
                obj['dist'].append(4)
                obj['constant'].append(fractures[i]['constant']['value'])
    return obj

