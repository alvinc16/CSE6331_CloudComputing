import pandas as pd
import numpy as np

# dummy_data = np.array([
#     ['Chris', 100000, '550', '1000010', 'chris.jpg', 'Chris is very smart'],
#     ['Jason', 99099, '420', None, 'jason.jpg', 'Jason also smart'],
#     ['Someone', 42000, None, '1000011', 'someone.jpg', 'Who is this'],
#     ['Dave', 1, 525, -0, None, 'Doesn\'t seem to nice']
# ])
# df = pd.DataFrame(dummy_data, columns=['Name', 'Salary', 'Room', 'Telnum', 'Picture', 'Keywords'])

dummy_data = np.array([
    ['Chris', 1, '550', '1000010', 'chris.jpg', 'Chris is very smart'],
    ['Jason', 2, '420', None, 'jason.jpg', 'Jason also smart'],
    ['Someone', 2, None, '1000011', 'someone.jpg', 'Who is this'],
    ['Dave', 1, 525, -0, None, 'Doesn\'t seem to nice']
])
df = pd.DataFrame(dummy_data, columns=['Name', 'Height', 'Author', 'Picture', 'Keywords'])

df.to_csv('./dummpy_data.csv', index=False)
