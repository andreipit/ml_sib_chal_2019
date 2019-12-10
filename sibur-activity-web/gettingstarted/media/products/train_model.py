import pandas as pd
from datetime import date, datetime, timedelta
from sklearn.model_selection import KFold
import lightgbm as lgb
import pickle

RS = 2734

def get_data(last_date):
    train_data = pd.read_csv('train.csv', parse_dates=['date'], index_col='date')
    # train_data = pd.read_csv('/kaggle/input/activity_train.csv.zip', parse_dates=['date'], index_col='date', compression='zip')
    train_data.drop(['atactic_1', 'atactic_2', 'atactic_3', 'f28','f25','f42'], axis=1, inplace=True)
    
    # Cмещаем все кроме таргета на 6 часов вперед
    train_data.iloc[:,:-1] = train_data.iloc[:,:-1].shift(6, freq='H')
    
    # Удаляем пустые строки
    train_data = train_data[train_data.notnull().all(axis=1)]
    
    # Берем последние N строк до определнной даты
    train_data = train_data[:last_date][-100_000:]
    
    # Отделяем таргет
    train_targets = train_data[['activity']]
    train_data.drop('activity', axis=1, inplace=True)

    print(last_date, train_data.shape, train_targets.shape)

    return train_data, train_targets

def LGB_kfold(data, labels, param, n_splits):
    kf = KFold(n_splits=n_splits)
    
    models = []    
    for fold, (train_indx, val_indx) in enumerate(kf.split(labels)):
        print(f'Fold {fold+1}')
        train_set = lgb.Dataset(data.iloc[train_indx], label=labels.iloc[train_indx])
        val_set = lgb.Dataset(data.iloc[val_indx], label=labels.iloc[val_indx])
        model = lgb.train(param, train_set, valid_sets=val_set, verbose_eval=500)
        models.append(model)
    
    return models

param = {
    'application': 'regression',
    'boosting': 'gbdt',
    'metric': 'mape',
    'num_leaves': 80,
    'max_depth': 9,
    'learning_rate': 0.02,
    'bagging_fraction': 0.85,
    'feature_fraction': 0.8,
    'min_split_gain': 0.02,
    'min_child_samples': 150,
    'min_child_weight': 0.02,
    'lambda_l2': 0.05,
    'verbosity': -1,
    'data_random_seed': 17,
    'early_stop': 100,
    'verbose_eval': 100,
    'num_rounds': 100
}

n_splits = 3

def daterange(start_date, end_date):
    for n in range(int ((end_date - start_date).days)):
        yield start_date + timedelta(n)

start_date = date(2018, 11, 1)
end_date = date(2018, 12, 30)

for single_date in daterange(start_date, end_date):
    last_date = single_date.strftime('%Y-%m-%d')
    X, y = get_data(last_date)
    
    LGB_result = LGB_kfold(X, y, param, n_splits)
    
    with open(f'models/model_{last_date}.pkl', 'wb') as f:
        pickle.dump(LGB_result, f)
