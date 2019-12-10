import pandas as pd
from datetime import date, datetime, timedelta
from sklearn.model_selection import KFold
import lightgbm as lgb
import pickle
import os
import time
import glob

RS = 2734

# print('pred started')

# Загружаем последнюю модель
def get_last_model(period):
  last_d = datetime(1900, 1, 1) 

  for f in glob.glob(f'models\{period}\*.pkl'):
    d2 = datetime.strptime(f.split('_')[2].split('.')[0], '%Y-%m-%d')

    if d2 > last_d:
      last_d = d2
      with open(f, 'rb') as f:
        models = pickle.load(f)
      
  # print('last_model:', period, '-', last_d)

  return models

models_dict = {
  'kat_15m':get_last_model('kat_15m'),
  'kat_3h':get_last_model('kat_3h'),
  'kat_6h':get_last_model('kat_6h'),
}



# Загружаем последний месяца из трейна
data = pd.read_csv('train.csv', parse_dates=['date'], index_col='date')
data.drop(['atactic_1', 'atactic_2', 'atactic_3', 'f28','f25','f42'], axis=1, inplace=True)

data = data['2018-12':]
f_cols = data.columns[:-1]
all_cols = list(data.columns)



# Для каждой строки...
for i in range(data.shape[0]):
  # Считываем существующие данные
  if os.path.exists('train_with_pred2.csv'):
      pred_file = pd.read_csv('train_with_pred2.csv', index_col='date', parse_dates=['date'])
  else:
      pred_file = pd.DataFrame(columns=['date'] + all_cols + ['pred6h']).set_index('date')

  # Выполняем предсказание
  predict = {}
  for period in models_dict:
    predict1 = models_dict[period][0].predict(data.iloc[[i]][f_cols])
    predict2 = models_dict[period][1].predict(data.iloc[[i]][f_cols])
    predict3 = models_dict[period][2].predict(data.iloc[[i]][f_cols])
    predict[period] = round((predict1[0] + predict2[0] + predict3[0]) / 3, 6)
    # print(period, data.iloc[i].name, predict[period])

  # Записываем новые предсказания
  pred_file.loc[data.iloc[i].name, all_cols] = data.iloc[i].values
  pred_file.loc[data.iloc[i].name + timedelta(hours=0.25), 'pred15m'] = predict['kat_15m']
  pred_file.loc[data.iloc[i].name + timedelta(hours=3), 'pred3h'] = predict['kat_3h']
  # pred_file.loc[data.iloc[i].name + timedelta(hours=6), 'pred6h'] = predict['kat_6h']
  pred_file.loc[data.iloc[i].name + timedelta(hours=6), 'pred6h'] = predict['kat_6h']*10-340

  # Если существуют параметры, выполняем для них предсказание
  if os.path.exists('setting.csv'):
      # Считываем параметры и заменяем в копии существющих значений
      setting = pd.read_csv('setting.csv', index_col=None)
      setting_cols = list(setting.columns)
      data_new = data.iloc[[i]].copy()
      data_new.loc[:, setting_cols] = setting.values
      
      predict = {}
      for period in models_dict:
          predict1 = models_dict[period][0].predict(data_new)
          predict2 = models_dict[period][1].predict(data_new)
          predict3 = models_dict[period][2].predict(data_new)
          predict[period] = round((predict1[0] + predict2[0] + predict3[0]) / 3, 6)
          # print(' -', period, data.iloc[i].name, predict[period])

      pred_file.loc[data.iloc[i].name + timedelta(hours=0.25), 'pred15m_new'] = predict['kat_15m']
      pred_file.loc[data.iloc[i].name + timedelta(hours=3), 'pred3h_new'] = predict['kat_3h']
      pred_file.loc[data.iloc[i].name + timedelta(hours=6), 'pred6h_new'] = predict['kat_6h']

  pred_file = pred_file.sort_index().fillna(0)
  pred_file[-3000:].to_csv('train_with_pred2.csv')

  # Ждем "минуту" и повторяем
  if i > 360:
      time.sleep(3)