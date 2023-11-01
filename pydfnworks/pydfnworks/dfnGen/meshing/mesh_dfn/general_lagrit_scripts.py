def define_zones():
    """Processes zone files for particle tracking. All zone files are combined into allboundaries.zone 
    
    Parameters
    ----------
        None

    Returns
    -------
        None

    Notes
    -----
        None 
    """

    with open("allboundaries.zone", "w") as fall:
        #copy all but last 2 lines of boundary_top.zone in allboundaries.zone
        fzone = open("boundary_top.zone", "r")
        lines = fzone.readlines()
        lines = lines[:-2]
        fzone.close()
        fall.writelines(lines)
        #copy all but frist and last 2 lines of boundary_bottom.zone in allboundaries.zone
        files = ['bottom', 'left_w', 'front_n', 'right_e']
        for filename in files:
            with open(f"boundary_{filename}.zone", "r") as fzone:
                lines = fzone.readlines()
                lines = lines[1:-2]
            fall.writelines(lines)
        fzone = open("boundary_back_s.zone", "r")
        lines = fzone.readlines()
        lines = lines[1:]
        fzone.close()
        fall.writelines(lines)

