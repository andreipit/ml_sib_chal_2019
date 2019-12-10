import pandas as pd
from datetime import date, datetime, timedelta
from tqdm import tqdm_notebook as tqdm
from sklearn.model_selection import KFold
import lightgbm as lgb
import pickle
import os
import time
import glob

RS = 2734


# Загружаем последнюю модель
last_d = datetime(1900, 1, 1) 

for f in glob.glob('models/*.pkl'):
  d2 = datetime.strptime(f.split('_')[1].split('.')[0], '%Y-%m-%d')

  if d2 > last_d:
    last_d = d2
    with open(f, 'rb') as f:
      models = pickle.load(f)
    
    # print(d2)
    
# Загружаем последний месяца из трейна
data = pd.read_csv('train.csv', parse_dates=['date'], index_col='date')
data.drop(['atactic_1', 'atactic_2', 'atactic_3', 'f28','f25','f42'], axis=1, inplace=True)

data = data['2018-12':]
cols = data.columns[:-1]


# Для каждой строки...
for i in range(data.shape[0]):
  # Выполняем предсказание
  predict1 = models[0].predict(data.iloc[[i]][cols])
  predict2 = models[1].predict(data.iloc[[i]][cols])
  predict3 = models[2].predict(data.iloc[[i]][cols])

  predict = round((predict1[0] + predict2[0] + predict3[0]) / 3, 6)
  # print(predict)

  # Считываем существующие данные
  if os.path.exists('train_with_pred2.csv'):
      pred_file = pd.read_csv('train_with_pred2.csv', index_col='date')
  else:
      pred_file = pd.DataFrame(columns=['date','activity','pred6h']).set_index('date')

  # Записываем новые предсказания
  pred_file.loc[data.iloc[[i]].index[0]] = [data.iloc[[i]]['activity'][0], predict]
  pred_file.to_csv('train_with_pred2.csv')

  # Ждем "минуту" и повторяем
  time.sleep(1)