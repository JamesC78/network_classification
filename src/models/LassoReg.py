import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import Lasso
import matplotlib.pyplot as plt

infile = 'C:/Users/Owner/Documents/VERUM/Network stuff/git/src/data/data_minmaxscale.csv' # --- change this for specific machine
df = pd.read_csv(infile, index_col=0)

X = df.drop(['Graph', 'Collection'], axis=1).values
y1 = df['Collection'].values

y = df.Collection.astype('category').cat.codes.values

lasso = Lasso(alpha=0.1)

lasso_coef = lasso.fit(X, y).coef_

name = df.columns.values
index = [0, 1]

names = np.delete(name, index)

plt.plot(range(len(names)), lasso_coef)
plt.xticks(range(len(names)), names, rotation=60)
plt.ylabel = ('Coefficients')
plt.show()