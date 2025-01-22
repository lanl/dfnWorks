# automatically changes path names in tests directory and pydfnworks

import os

old = 'DUMMY'
new = os.path.join('/',*os.getcwd().split('/')[:-3])

def listdir_recursive(base_directory):
    ''' List files

    Parameters
    ----------
        base_directory : string
            base directory

    Returns
    -------
        files : list
            list of files

    Notes
    -----
    None
    '''
    files = []
    for root, directories, filenames in os.walk(base_directory):
        for filename in filenames: 
                files.append(os.path.join(root,filename))
    return files

def replace(old, new):
    ''' Replace ext

    Parameters
    ----------
        old : string
            old text to replace

        new : string
            new text to overwrite with

    Returns
    -------
        None

    Notes
    -----
    None
    '''
    files = listdir_recursive('../')
    files.extend(listdir_recursive('../../examples'))

    for file in files:

        if 'fix_paths' in file:
            continue

        try:
            with open(file,'r') as f:
                replaced_text = f.read().replace(old,new)
        except UnicodeDecodeError:
            continue

        with open(file,'w') as f:
            f.write(replaced_text)

print(new)
print('replacing ', old, ' with ', new)
replace(old, new)
