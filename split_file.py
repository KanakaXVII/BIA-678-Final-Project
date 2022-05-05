import sys
import pandas as pd
import os

# Read the file
entire = pd.read_csv('train.csv', header=None)
print(entire.iloc[3599999])
sys.exit(1)

# Make splits in the df
inds = list(range(0, len(entire) + 1, 600000))
old_ind = 0

# Write based on file counter
for i, j in enumerate(inds):
    if i != 0:
        new_df = entire.iloc[old_ind:j]
        old_ind = j
        
        file_name = f'train_{i}.csv'
        new_df.to_csv(file_name, index=False)