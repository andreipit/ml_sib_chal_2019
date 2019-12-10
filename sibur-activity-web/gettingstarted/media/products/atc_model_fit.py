import numpy as np
import pandas as pd
from sklearn.linear_model import ARDRegression
from tqdm import tqdm
import pickle

def get_data(period_lag, period_term):
    data = pd.read_csv('train.csv', parse_dates=['date'], index_col='date')
    data = data[:'2018-12-30']

    targets = data[['atactic_1', 'atactic_2', 'atactic_3']].copy()
    data = data.iloc[:,:-4]
    data.drop('f28', axis=1, inplace=True)
    
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
    all_features = data.join(all_features)

    # Исходные таргет и данные
    atactic_tr_targets = targets.loc[targets.notnull().all(axis=1)]
    atactic_tr_data = all_features.shift(period_lag, freq=period_term).loc[atactic_tr_targets.index]

    # Объединяем таргет и данные
    atactic_tr = atactic_tr_targets.join(atactic_tr_data).dropna()

    return atactic_tr


def train_model(df, TARGET, PARAM, corr_rank):
    corrs = df.corr().loc[TARGET, df.columns[3:]]
    corrs_cols = corrs[corrs.abs() <= corr_rank].index
    FCOLS = [col for col in df.columns[3:] if col not in corrs_cols]
    #print(len(FCOLS))
    
    model = ARDRegression(**PARAM)
    model.fit(df[FCOLS], df[TARGET])
    
    return model, FCOLS

def get_atc_models(data):
    TARGET = 'atactic_1'
    PARAM = {'alpha_1': 0.01, 'alpha_2': 0.0001, 'lambda_1': 0.0001, 'lambda_2': 0.1, 'threshold_lambda': 500}
    model1, col1 = train_model(data, TARGET, PARAM, 0.45)

    TARGET = 'atactic_2'
    PARAM = {'alpha_1': 0.0001, 'alpha_2': 0.0001, 'lambda_1': 0.01, 'lambda_2': 0.001, 'threshold_lambda': 500}
    model2, col2 = train_model(data, TARGET, PARAM, 0.4)

    TARGET = 'atactic_3'
    PARAM = {'alpha_1': 0.0001, 'alpha_2': 0.0001, 'lambda_1': 0.1, 'lambda_2': 0.0001, 'threshold_lambda': 1000}
    model3, col3 = train_model(data, TARGET, PARAM, 0.3)
    
    return [model1, model2, model3, col1, col2, col3]

data = get_data(15, 'min')
models = get_atc_models(data)
with open(f'models/atc/model_15m.pkl', 'wb') as f:
    pickle.dump(models, f)

data = get_data(3, 'H')
models = get_atc_models(data)
with open(f'models/atc/model_3H.pkl', 'wb') as f:
    pickle.dump(models, f)

data = get_data(6, 'H')
models = get_atc_models(data)
with open(f'models/atc/model_6H.pkl', 'wb') as f:
    pickle.dump(models, f)