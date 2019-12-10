import pandas as pd
from datetime import date, datetime, timedelta
from sklearn.linear_model import ARDRegression
from tqdm import tqdm
import pickle
import os
import time
import glob


# Загружаем модели
def get_last_model(period):
    with open(f'models/atc/model_{period}.pkl', 'rb') as f:
        model = pickle.load(f)
    
    return model

models_dict = {
  'atc_15m': get_last_model('15m'),
  'atc_3h': get_last_model('3H'),
  'atc_6h': get_last_model('6H'),
}

# Загружаем последние два дня из трейна
data = pd.read_csv('train.csv', parse_dates=['date'], index_col='date')
data_target = data['2018-12-31':].iloc[:,-3:].dropna()
data = data['2018-12-30':].iloc[:,:-4]
data.drop('f28', axis=1, inplace=True)


# Формируем для последнего дня (после 08:00) новые фичи
PERIODS = ['1H', '3H', '6H']
AGGREGATES = ['mean', 'median', 'std', 'max', 'min']

all_features = []

pbar = tqdm(total=(len(PERIODS) * len(AGGREGATES)))

for period in PERIODS:
    for agg in AGGREGATES:
        rolling_features = data.rolling(period).aggregate(agg)
        rolling_features.rename(lambda x: f'{x}_{period}_{agg}', axis=1, inplace=True)
        all_features.append(rolling_features)

        pbar.update(1)

all_features = pd.concat(all_features, axis=1)

data = data.join(all_features)
data = data['2018-12-31 08:01:00':]


f_cols = list(data.columns)

# Для каждой строки...
for i in range(data.shape[0]):
    # Считываем существующие данные
    if os.path.exists('atc_pred.csv'):
        pred_file = pd.read_csv('atc_pred.csv', index_col='date', parse_dates=['date'])
    else:
        pred_file = pd.DataFrame(columns=['date'] + f_cols + list(data_target.columns)).set_index('date')
    
    a1_predict_15m = models_dict['atc_15m'][0].predict(data.iloc[[i]][models_dict['atc_15m'][3]])
    a2_predict_15m = models_dict['atc_15m'][1].predict(data.iloc[[i]][models_dict['atc_15m'][4]])
    a3_predict_15m = models_dict['atc_15m'][2].predict(data.iloc[[i]][models_dict['atc_15m'][5]])
    
    a1_predict_3h = models_dict['atc_3h'][0].predict(data.iloc[[i]][models_dict['atc_3h'][3]])
    a2_predict_3h = models_dict['atc_3h'][1].predict(data.iloc[[i]][models_dict['atc_3h'][4]])
    a3_predict_3h = models_dict['atc_3h'][2].predict(data.iloc[[i]][models_dict['atc_3h'][5]])
    
    a1_predict_6h = models_dict['atc_6h'][0].predict(data.iloc[[i]][models_dict['atc_6h'][3]])
    a2_predict_6h = models_dict['atc_6h'][1].predict(data.iloc[[i]][models_dict['atc_6h'][4]])
    a3_predict_6h = models_dict['atc_6h'][2].predict(data.iloc[[i]][models_dict['atc_6h'][5]])
    
    pred_file.loc[data.iloc[i].name, f_cols] = data.iloc[i].values
    pred_file.loc[data.iloc[i].name + timedelta(hours=0.25), 'a1_pred15m'] = a1_predict_15m[0]
    pred_file.loc[data.iloc[i].name + timedelta(hours=0.25), 'a2_pred15m'] = a2_predict_15m[0]
    pred_file.loc[data.iloc[i].name + timedelta(hours=0.25), 'a3_pred15m'] = a3_predict_15m[0]
    pred_file.loc[data.iloc[i].name + timedelta(hours=0.25), list(data_target.columns)] = data_target.iloc[0].values
    
    pred_file.loc[data.iloc[i].name + timedelta(hours=3), 'a1_pred3h'] = a1_predict_3h[0]
    pred_file.loc[data.iloc[i].name + timedelta(hours=3), 'a2_pred3h'] = a2_predict_3h[0]
    pred_file.loc[data.iloc[i].name + timedelta(hours=3), 'a3_pred3h'] = a3_predict_3h[0]
    
    pred_file.loc[data.iloc[i].name + timedelta(hours=6), 'a1_pred6h'] = a1_predict_6h[0]
    pred_file.loc[data.iloc[i].name + timedelta(hours=6), 'a2_pred6h'] = a2_predict_6h[0]
    pred_file.loc[data.iloc[i].name + timedelta(hours=6), 'a3_pred6h'] = a3_predict_6h[0]
    
    pred_file = pred_file.sort_index().fillna(0)
    pred_file[-3000:].to_csv('atc_pred.csv')
    
    time.sleep(3)