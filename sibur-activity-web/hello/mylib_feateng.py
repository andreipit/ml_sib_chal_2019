# from catalog.models import Category, Product
# from about.models import Parameter
from django.utils import timezone
import os
from django.conf import settings
import pdb #pdb.set_trace()
from django.http import HttpResponse
# from django.core.cache import cache # This is the memcache cache.
from django.core.cache import cache # This is the memcache cache.
import numpy as np


import pathlib
import time
import tqdm
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os,sys,inspect,pickle,json,time,datetime,re
import random as rn
import lightgbm as lgb


def convert_to_input_predict(df, model):
    TARGET = 'activity'



    train_data_web = df
    train_targets_web = train_data_web[["activity"]].copy() ;print('train_targets_web',train_targets_web.shape)
    train_data_web.drop(["f28","activity","atactic_1","atactic_2","atactic_3"], axis=1, inplace=True)
    data_web = train_data_web #pd.concat([train_data[test_data.columns], test_data]) ;print('data',data.shape) # use all columns except 4 targets

    # generate 825 new cols from joineddata
    # data.drop('ТЭА (л/c)', axis=1, inplace=True) # 'f28' ## try without inplace!
    #train_data_web.drop("f28", axis=1, inplace=True)

    #ACOLS = ["atactic_1", "atactic_2", "atactic_3"]
    #not_null_atactic = train_targets.loc[train_targets[ACOLS].notnull().all(axis=1), ACOLS] ;print(not_null_atactic.shape)
    PERIODS = ["4H", "5H", "6H"]
    AGGREGATES = ["mean", "median", "std", "max", "min"]#, "sum"]
    #PERIODS = ["3H"]
    #AGGREGATES = ["mean"]
    all_features_web = []
    for period in PERIODS:#tqdm.tqdm_notebook(PERIODS):
        for agg in AGGREGATES:
            print(period,agg,end=',')
            rolling_features_web = data_web.rolling(period).aggregate(agg)
            rolling_features_web.rename(lambda x: "_".join([x, period, agg]), axis=1, inplace=True)
            all_features_web.append(rolling_features_web)
    all_features_web = pd.concat(all_features_web, axis=1) 
    print('all_features',all_features_web.shape) #825/5/3 = 55 #15 new cols for each of 55 features 



    full_data_web = data_web.join(all_features_web) ;print('full_data_web',full_data_web.shape)  # (566709, 880)



    activity_train_with_nulls_web = full_data_web #train_targets[["activity"]].join(full_data.shift(6, freq="H")) ;print('activity_train_with_nulls',activity_train_with_nulls.shape) # add 6 hours empty rows to start, delete last 6 hours rows
    activity_train_web = activity_train_with_nulls_web[activity_train_with_nulls_web.notnull().all(axis=1)] ;print('activity_train_web',activity_train_web.shape)



    train_data_web = activity_train_web
    print('train_data_web',train_data_web.shape)

    train_web = train_data_web

    def split_cols_np_web(test):
        x_test  = test.values
        return x_test

    x_train_web = split_cols_np_web(train_web) ;print('x_train_web',x_train_web.shape)




    def normalize_by_train_web(x_train, train):
        #center, scale = train.iloc[:, 1:].mean().values, train.iloc[:, 1:].std().values
        center_x, scale_x = train.mean().values, train.std().values
        #center_x, scale_x = train.drop(TARGET, axis=1, inplace=False).mean().values, train.drop(TARGET, axis=1, inplace=False).std().values
    #     center_y, sca/le_y = train[TARGET].mean(), train[TARGET].std()
        x_train_n = (x_train - center_x)/scale_x
    #     x_val_n   = (x_val   - center_x)/scale_x
    #     x_test_n  = (x_test  - center_x)/scale_x
    #     y_train_n = (y_train - center_y)/scale_y
    #     y_val_n   = (y_val   - center_y)/scale_y
        #print('x_train_n',x_train_n.shape, 'y_train_n',y_train_n.shape, 'x_val_n',x_val_n.shape, 'y_val_n', y_val_n.shape)
        return x_train_n
    x_train_n_web = normalize_by_train_web(x_train_web, train_web) ;print('x_train_n_web',x_train_n_web.shape)






    y_train_pred_n_web = model.predict(x_train_n_web) #;print('y_train_pred_n_web',y_train_pred_n_web.shape)

    def denormalize_by_train(y_train_pred_n, train, TARGET):
        y_train_pred = y_train_pred_n * train[TARGET].std() + train[TARGET].mean()
        return y_train_pred
    y_train_pred_web = denormalize_by_train(y_train_pred_n_web, train_targets_web, TARGET) ;print('y_train_pred_n_web',y_train_pred_n_web.shape)

    return y_train_pred_web


    # return model.predict(np.random.rand(1,880))
