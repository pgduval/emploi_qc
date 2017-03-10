import pandas as pd
import os
import matplotlib.pyplot as plt
import datetime

PATH = '/home/elmaster/project/emploi_qc'

date = datetime.datetime.now().strftime("%Y-%m-%d")
data = pd.read_csv(os.path.join(PATH, 'output', 'villes_{}.csv'.format(date)))


data2 = data.groupby(['city_name', 'appelation']).agg({'n_poste': 'count'})

data2 = (data.groupby(['appelation', 'scolarite'])
             .agg({'n_poste': 'count'})
             .sort_values('n_poste', ascending=False)
         )

print(data2)