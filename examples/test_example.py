import pandas as pd
import sys
import difflib
from datetime import datetime
import os

try:
    example_name = sys.argv[1]
except:
    example_name = None
    pass

df = pd.read_pickle('examples.p')

if example_name:
    current = df.loc[df['example'] == example_name]
    if current.empty:
        print(f'Unknown example name {example_name}')
        example_list = df['example']
        close = difflib.get_close_matches(example_name, example_list)
        if len(close) > 0:
            print('did you mean:')
            for c in close:
                print(c)
        sys.exit(1)
    else:
        print(current)
        idx = current.index[0]
        df['complete'][idx] = True
        df['date'][idx] = datetime.now()
        df['tester'][idx] = os.getlogin()
        print(df)

print("\nExamples Checked")
complete = df.loc[df['complete'] == True]
print(complete)

print("\nExamples Remaining")
incomplete = df.loc[df['complete'] == False]
print(incomplete)

df.to_pickle('examples.p')
