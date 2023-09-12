import os
rootdir=('/Users/jhyman/src/dfnworks-jdhdev/pydfnworks')
for folder, dirs, files in os.walk(rootdir):
    for file in files:
        if file.endswith('.py'):
            fullpath = os.path.join(folder, file)
            with open(fullpath, 'r') as f:
                for line in f:
                    if "PYTHON_EXE" in line:
                        print(fullpath)
                        break