from django.shortcuts import render
from django.http import HttpResponse

from .models import Greeting
import requests
from django.conf import settings

import xlrd
import hello.mylib as mylib
import hello.mylib_feateng as mylib_feateng

from django.http import HttpResponseRedirect
import pdb #pdb.set_trace()
import pandas as pd

def uploadcsv(request): # pdb.set_trace();
    import pickle
    context = {'predictions': 'uploadcsv2','df': 'uploadcsv2','pred': 'uploadcsv2'}
    return render(request, "index.html", context)

def update(request):
    import pickle

    # activity
    filepath = settings.MEDIA_ROOT + '/products/'+ 'train_with_pred2' + '.csv'
    # filepath = settings.MEDIA_ROOT + '/products/'+ 'train_with_pred_backup' + '.csv'
    df = pd.read_csv(filepath, parse_dates=["date"], index_col="date").tail(460)#df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    result = []
    result.append(['date', 'true', 'prediction'])
    for i in range(df.shape[0]):
        if df.iloc[i]['activity'] == 0: activity = 0
        else: activity = df.iloc[i]['activity']
        if df.iloc[i]['pred6h'] == 0: pred6h = 0
        else: pred6h = df.iloc[i]['pred6h']
        result.append([str(df.index[i]).split(' ')[1], activity, pred6h])

    # atactic
    # atc_filepath = settings.MEDIA_ROOT + '/products/'+ 'atc_pred' + '.csv'
    # atc_df = pd.read_csv(atc_filepath, parse_dates=["date"], index_col="date").tail(720)#df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    # atc_result = []
    # # atc_result.append(['date', 'true1', 'true2', 'true3', 'prediction1', 'prediction2', 'prediction3'])
    # atc_result.append(['date', 'true1', 'prediction1'])
    # for i in range(atc_df.shape[0]):
    #     atc1 = df.iloc[i]['atactic_1']
    #     # atc2 = df.iloc[i]['atactic_2']
    #     # atc3 = df.iloc[i]['atactic_3']
    #     a1_pred6h = df.iloc[i]['a1_pred6h']
    #     # a2_pred6h = df.iloc[i]['a2_pred6h']
    #     # a3_pred6h = df.iloc[i]['a3_pred6h']
    #     # atc_result.append([str(df.index[i]), atc1, atc2, atc3, a1_pred6h, a2_pred6h, a3_pred6h])
    #     atc_result.append([str(df.index[i]), atc1, a1_pred6h])

    # # atactic fake
    # filepath = settings.MEDIA_ROOT + '/products/'+ 'train_with_pred2' + '.csv'
    # df = pd.read_csv(filepath, parse_dates=["date"], index_col="date").tail(720)#df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    # atc_result = []
    # atc_result.append(['date', 'true', 'prediction'])
    # for i in range(df.shape[0]):
    #     if df.iloc[i]['activity'] == 0: activity = 0
    #     else: activity = df.iloc[i]['activity']
    #     if df.iloc[i]['pred6h'] == 0: pred6h = 0
    #     else: pred6h = df.iloc[i]['pred6h']
    #     atc_result.append([str(df.index[i]), activity, pred6h])
    values = [round(df.head(1)['f0'][-1],2), round(df.head(1)['f1'][-1],2), round(df.head(1)['f7'][-1],2), round(df.head(1)['f14'][-1],2), round(df.head(1)['f41'][-1],2), round(df.head(1)['f50'][-1],2)]
    import json
    # response = HttpResponse(json.dumps({'product_values_count': '123', 'prediction':result, 'atc_prediction':atc_result}))
    response = HttpResponse(json.dumps({'product_values_count': '123', 'prediction':result,'values':values}))
    return response

    # context = {'predictions': 'update','df': 'update','pred': 'update'}
    # return render(request, "index.html", context)

def atc_update(request):
    import pickle

    # atactic
    # atc_filepath = settings.MEDIA_ROOT + '/products/'+ 'atc_pred' + '.csv'
    # atc_df = pd.read_csv(atc_filepath, parse_dates=["date"], index_col="date").tail(720)#df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    # atc_result = []
    # # atc_result.append(['date', 'true1', 'true2', 'true3', 'prediction1', 'prediction2', 'prediction3'])
    # atc_result.append(['date', 'true1', 'prediction1'])
    # for i in range(atc_df.shape[0]):
    #     atc1 = atc_df.iloc[i]['atactic_1']
    #     # atc2 = df.iloc[i]['atactic_2']
    #     # atc3 = df.iloc[i]['atactic_3']
    #     a1_pred6h = atc_df.iloc[i]['a1_pred6h']
    #     # a2_pred6h = df.iloc[i]['a2_pred6h']
    #     # a3_pred6h = df.iloc[i]['a3_pred6h']
    #     # atc_result.append([str(df.index[i]), atc1, atc2, atc3, a1_pred6h, a2_pred6h, a3_pred6h])
    #     atc_result.append([str(atc_df.index[i]), atc1, a1_pred6h])

    # atactic fake
    # filepath = settings.MEDIA_ROOT + '/products/'+ 'train_with_pred2' + '.csv'
    # df = pd.read_csv(filepath, parse_dates=["date"], index_col="date").tail(360)#df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    # atc_result = []
    # atc_result.append(['date', 'true', 'prediction'])
    # for i in range(df.shape[0]):
    #     if df.iloc[i]['activity'] == 0: activity = 0
    #     else: activity = df.iloc[i]['activity']
    #     if df.iloc[i]['pred6h'] == 0: pred6h = 0
    #     else: pred6h = df.iloc[i]['pred6h']
    #     atc_result.append([str(df.index[i]), activity, pred6h])

    atc_result = []
    atc_result.append(['date', 'true', 'prediction'])
    atc_result.append(['2012-12-01', '10', '20'])


    import json
    response = HttpResponse(json.dumps({'product_values_count': '123', 'atc_prediction':atc_result}))
    return response

    # context = {'predictions': 'update','df': 'update','pred': 'update'}
    # return render(request, "index.html", context)    

def index(request):
    import pickle
    imgs_adress = settings.STATIC_ROOT + '\\hello\\hello_imgs\\'
    context = {'predictions': 'index','df': 'index','pred': 'index','imgs_adress':imgs_adress, 'values':[12,13,14,15,16,17]}
    filepath = settings.MEDIA_ROOT + '/products/'+ 'train_with_pred2' + '.csv'
    df = pd.read_csv(filepath, parse_dates=["date"], index_col="date") #df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    true_values = []; predictions = []; dates = []
    for i in range(df.shape[0]):
        true_values.append(df.iloc[i]['activity'])
        predictions.append(df.iloc[i]['pred6h'])    
        dates.append(str(df.index[i]))
    result = (true_values, predictions, dates)
    context['df'] = result#str(df.head(1000))
    context['values'] = [df['f0'][-1],df['f1'][-1],df['f2'][-1],df['f3'][-1],df['f4'][-1],df['f5'][-1]]
    return render(request, "index_boot.html", context)

def atc_index(request):
    import pickle
    imgs_adress = settings.STATIC_ROOT + '\\hello\\hello_imgs\\'
    context = {'predictions': 'index','df': 'index','pred': 'index','imgs_adress':imgs_adress, 'values':[12,13,14,15,16,17]}
    filepath = settings.MEDIA_ROOT + '/products/'+ 'train_with_pred2' + '.csv'
    df = pd.read_csv(filepath, parse_dates=["date"], index_col="date") #df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    true_values = []; predictions = []; dates = []
    for i in range(df.shape[0]):
        true_values.append(df.iloc[i]['activity'])
        predictions.append(df.iloc[i]['pred6h'])    
        dates.append(str(df.index[i]))
    result = (true_values, predictions, dates)
    context['df'] = result#str(df.head(1000))
    context['values'] = [df['f0'][-1],df['f1'][-1],df['f2'][-1],df['f3'][-1],df['f4'][-1],df['f5'][-1]]
    return render(request, "index_atactic.html", context)

def db(request): # pdb.set_trace();
    import pickle
    context = {'predictions': 'db','df': 'db','pred': 'db'}
    return render(request, "index.html", context)





