#### A fully-coupled T-H simulation of
#### cold water injection into a hot reservoir
############################################################
# Trial pressure controls for the 400 m open intervals.  These are absolute
# bottomhole pressures.  The resulting rates are model outputs. 
# injection BHP > initial reservoir pressure > production BHP
injection_bhp = 40000000.0 # Pa
production_bhp = 20000000.0 # Pa

[Mesh]
  [generated]
    type = FileMeshGenerator
    file = 'dfm_mesh/dfm_tet_mesh_w_fsets.exo'
  []
  [meters]
    type = TransformGenerator
    input = generated
    transform = SCALE
    vector_value = '1000 1000 1000'
  []
  
  [fractures]
    type = LowerDBlockFromSidesetGenerator
    input = meters
    sidesets = '1 2 3 4'
    new_block_id = 2
    new_block_name = fractures
  []

  [injection_line_node]
    input = fractures
    type = BoundingBoxNodeSetGenerator
    new_boundary = injection_line
    bottom_left = '175 -25 -275'
    top_right = '225 25 -125'
  []
[]

############################################################
[GlobalParams]
  PorousFlowDictator = dictator
  gravity = '0 0 -9.8'
[]

[PorousFlowFullySaturated]
  coupling_type = ThermoHydro
  porepressure = P
  temperature = T
  fp = fluid
  temperature_unit = Kelvin
  stabilization = full
[]

############################################################
[Variables]
  [./P]
  [../]
  [./T]
    scaling = 1E-6
  [../]
[]

############################################################
[ICs]
  [./P]
    type = FunctionIC
    function =  '101325 + 9.8*1000*3000 - 9.8*1000*z'
    variable = P
  [../]
  [./T]
    type = FunctionIC
    function =  '200 - 60*z/1000 + 273'
    variable = T
  [../]
[]

############################################################
[Functions]
  # Ramp both wells on over the first two days to avoid an impulsive startup.
  # Peaceman's sign convention is negative for injection and positive for production.
  [./injection_character]
    type = PiecewiseLinear
    x = '0 172800'
    y = '0 -1'
  [../]

  [./production_character]
    type = PiecewiseLinear
    x = '0 172800'
    y = '0 1'
  [../]

  [./injection_bottomhole_pressure]
    type = ConstantFunction
    value = ${injection_bhp}
  [../]

  [./production_bottomhole_pressure]
    type = ConstantFunction
    value = ${production_bhp}
  [../]

  # Convert PorousFlowSumQuantity kg-per-timestep output to kg/s.
  [production_mass_rate_function]
    type = ParsedFunction
    symbol_names = 'dt produced_mass'
    symbol_values = 'dt produced_mass_this_timestep'
    expression = 'produced_mass/dt'
  []

  [injection_mass_rate_function]
    type = ParsedFunction
    symbol_names = 'dt injected_mass'
    symbol_values = 'dt injected_mass_this_timestep'
    expression = '-injected_mass/dt'
  []
[]

[AuxVariables]
  [injection_temperature]
    initial_condition = 330
  []
[]

[FluidProperties]
  [./fluid]
    type = SimpleFluidProperties
    bulk_modulus = 2e9
    density0 = 1000
    thermal_expansion = 0.0002
    cv = 4180
    cp = 4180
    viscosity = 0.001
  [../]
[]

############################################################
# Explicit inline points avoid automatic line tracing on the mixed-dimensional mesh.
# Each vector lists one quantity at the three points; radius and coordinates are metres.
# Points run from top to bottom to preserve the bottomhole-pressure reference.
[Reporters]
  [injection_geometry]
    type = ConstantReporter
    real_vector_names = 'radius x y z'
    real_vector_values = '1 1 1;
                          200 200 200;
                          0 0 0;
                          -150 -200 -250'
  []
  [production_geometry]
    type = ConstantReporter
    real_vector_names = 'radius x y z'
    real_vector_values = '1 1 1;
                          -200 -200 -200;
                          0 0 0;
                          250 200 150'
  []
[]

[DiracKernels]
  # Pressure-controlled injection borehole with inline radius and coordinates.
  [./injection_water]
    type = PorousFlowPeacemanBorehole
    SumQuantityUO = injected_mass
    bottom_p_or_t = injection_bottomhole_pressure
    character = injection_character
    fluid_phase = 0
    # radius (m), x, y, z at the top of the interval
    weight_reporter = 'injection_geometry/radius'
    x_coord_reporter = 'injection_geometry/x'
    y_coord_reporter = 'injection_geometry/y'
    z_coord_reporter = 'injection_geometry/z'
    unit_weight = '0 0 -9800'
    use_mobility = true
    variable = P
  [../]

  # Pressure-controlled production borehole and its advected enthalpy sink.
  [./production_water]
    type = PorousFlowPeacemanBorehole
    SumQuantityUO = produced_mass
    bottom_p_or_t = production_bottomhole_pressure
    character = production_character
    fluid_phase = 0
    # radius (m), x, y, z at the top of the interval
    weight_reporter = 'production_geometry/radius'
    x_coord_reporter = 'production_geometry/x'
    y_coord_reporter = 'production_geometry/y'
    z_coord_reporter = 'production_geometry/z'
    unit_weight = '0 0 -9800'
    use_mobility = true
    variable = P
  [../]

  [./production_heat]
    type = PorousFlowPeacemanBorehole
    SumQuantityUO = produced_heat
    bottom_p_or_t = production_bottomhole_pressure
    character = production_character
    fluid_phase = 0
    use_enthalpy = true
    # radius (m), x, y, z at the top of the interval
    weight_reporter = 'production_geometry/radius'
    x_coord_reporter = 'production_geometry/x'
    y_coord_reporter = 'production_geometry/y'
    z_coord_reporter = 'production_geometry/z'
    unit_weight = '0 0 -9800'
    use_mobility = true
    variable = T
  [../]
[]

############################################################
[BCs]
  # A fixed injection-node temperature is the standard companion to a
  # pressure-controlled Peaceman injector in this 2-D formulation.
  [./injection_temperature]
    type = MatchedValueBC
    variable = T
    v = injection_temperature
    boundary = injection_line
  [../]
[]

############################################################
[UserObjects]
  [./pc]
    type = PorousFlowCapillaryPressureVG
    alpha = 1E-8
    m = 0.5
  [../]

  [./injected_mass]
    type = PorousFlowSumQuantity
  [../]

  [./produced_mass]
    type = PorousFlowSumQuantity
  [../]

  [./produced_heat]
    type = PorousFlowSumQuantity
  [../]

[]

############################################################
[Materials]
  [./rho]
    type = GenericConstantMaterial
    prop_names = density
    prop_values = 2500
  [../]

  [matrix_porosity]
    type = PorousFlowPorosityConst
    block = 1
    porosity = 0.01
  []
  [fracture_porosity]
    type = PorousFlowPorosityConst
    block = fractures
    porosity = 0.0005       # aperture * physical porosity
  []
  [matrix_permeability]
    type = PorousFlowPermeabilityConst
    block = 1
    permeability = '1e-15 0 0  0 1e-15 0  0 0 1e-15'
  []
  [fracture_permeability]
    type = PorousFlowPermeabilityConst
    block = fractures
    permeability = '1e-11 0 0  0 1e-11 0  0 0 1e-11'
  []

  [matrix_thermal_conductivity]
    type = PorousFlowThermalConductivityIdeal
    block = 1
    dry_thermal_conductivity = '2.75 0 0  0 2.75 0  0 0 2.75'
  []
  [fracture_thermal_conductivity]
    type = PorousFlowThermalConductivityIdeal
    block = fractures
    # aperture * physical fracture conductivity
    dry_thermal_conductivity = '0.0014 0 0  0 0.0014 0  0 0 0.0014'
  []

  [matrix_heat]
    type = PorousFlowMatrixInternalEnergy
    block = 1
    density = 2500
    specific_heat_capacity = 1200
  []
  [fracture_heat]
    type = PorousFlowMatrixInternalEnergy
    block = fractures
    density = 1.0
    specific_heat_capacity = 0
  []
[]

############################################################
[Postprocessors]
  ### EXTRACTION MONITORING ###
  [dt]
    type = TimestepSize
    outputs = none
  []

  [injected_mass_this_timestep]
    type = PorousFlowPlotQuantity
    uo = injected_mass
  []

  [produced_mass_this_timestep]
    type = PorousFlowPlotQuantity
    uo = produced_mass
  []

  [produced_heat_this_timestep]
    type = PorousFlowPlotQuantity
    uo = produced_heat
  []

  # Positive magnitudes in kg/s, averaged over the completed timestep.
  [injection_mass_rate]
    type = FunctionValuePostprocessor
    function = injection_mass_rate_function
    indirect_dependencies = 'dt injected_mass_this_timestep'
  []

  [production_mass_rate]
    type = FunctionValuePostprocessor
    function = production_mass_rate_function
    indirect_dependencies = 'dt produced_mass_this_timestep'
  []

  [T_production]
    type = VectorPostprocessorReductionValue
    vectorpostprocessor = production_temperature_line
    vector_name = T
    value_type = average
    execute_on = 'initial timestep_end'
  []
[]

[VectorPostprocessors]
  [production_temperature_line]
    type = LineValueSampler
    variable = T
    start_point = '-200 0 150'
    end_point = '-200 0 250'
    num_points = 3
    sort_by = y
    execute_on = 'initial timestep_end'
    outputs = none
  []
[]

############################################################
[Preconditioning]
  active = typically_efficient
  [typically_efficient]
    type = SMP
    full = true
    petsc_options_iname = '-pc_type -pc_hypre_type -pc_hypre_boomeramg_strong_threshold'
    petsc_options_value = ' hypre    boomeramg      0.7'
  []
[]

[Executioner]
  type = Transient
  solve_type = Newton
  dt = 172800
  end_time = 345600

  # Relaxed tolerances for faster convergence
  nl_rel_tol = 1e-5  # default 1e-8
  nl_abs_tol = 1e-6  # default 1e-50
  nl_max_its = 15    # default 50
  l_max_its = 50     # linear iterations
  l_tol = 1e-3       # linear tolerance (loose is fine)
[]

############################################################
[Outputs]
  file_base      = th_transient_out
  
  [./exodus]
    type = Exodus
    time_step_interval = 15 # every N time steps
    show = 'T P'  # Only save temperature and pressure
  [../]

  [./csv]
    type = CSV
    # time_step_interval = 15
  [../]

  [./console]
    type = Console
    output_linear = false
    output_nonlinear = false
  [../]
[]
############################################################
