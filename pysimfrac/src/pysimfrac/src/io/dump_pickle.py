import pickle 

def to_pickle(self, pickle_filename):
    """ Saves the DFN object into a pickle format

    Parameters
    --------------
        SimFrac Object
        pickle_filename : string 
            Name of file. 
    Returns
    ------------
        None

    Notes
    ------------
        None
    """
    import pickle

    print(f'--> Pickling simfrac object to {pickle_filename}')
    if os.path.isfile(pickle_filename):
        response = input(
            f"--> Warning {pickle_filename} exists. Are you sure you want to overwrite it?\nResponse [y/n]: "
        )
        if response == 'yes' or response == 'y':
            print('--> Overwritting file')
            pickle.dump(self, open(pickle_filename, "wb"))
            print(
                f'--> Pickling simfrac object to {pickle_filename} : Complete')
        elif response == 'no' or 'n':
            print("--> Not writting file.")
        else:
            print("Unknown Response. {response}.\nNot writting file.")
    else:
        pickle.dump(self, open(pickle_filename, "wb"))
        print(f'--> Pickling simfrac object to {pickle_filename} : Complete')


def from_pickle(self, filename):
    """ Loads the simfrac object from a pickle format

    Parameters
    --------------
        self : simfrac Object
        filename : string
            name of pickle DFN object 

    Returns
    ------------
        simfrac object 

    Notes
    ------------
        
    """
    import pickle
    tmp = pickle.load(open(filename, "rb"))
    self.__dict__ = tmp.__dict__.copy()


