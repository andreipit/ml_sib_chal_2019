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

def uploadcsv2(request): # pdb.set_trace();
    wb = xlrd.open_workbook(filename=None, file_contents=request.FILES['avatar'].read(), formatting_info=True) # https://xlrd.readthedocs.io/en/latest/api.html#module-xlrd.book
    sheet = wb.sheet_by_index(0)
    def save_xlrd_sheet_to_db(sheet):
        categories = mylib.read_xlslines_as_files_and_folders(sheet)
        Category.objects.all().delete()
        Product.objects.all().delete()
        mylib.reset_autoincrement(Category, Product)
        for cat in categories:
            c = Category(category_name=cat['category_name'], parent_category_id=categories[cat['parent_category_id']]['id'], pub_date=timezone.now())
            c.save()
            cat['id'] = c.id
            for prod in cat['products']:
                # we don`t need field 'photo' in table anymore
                # filepath = 'products/' + prod['product_code'] + '.jpg'
                # if os.path.isfile(settings.MEDIA_ROOT + '/' + filepath):   p = Product(category=c, product_code=prod['product_code'], product_name=prod['product_name'], product_price=prod['product_price'], pub_date=timezone.now(), product_photo=filepath)
                # else:                                                       p = Product(category=c, product_code=prod['product_code'], product_name=prod['product_name'], product_price=prod['product_price'], pub_date=timezone.now())
                p = Product(category=c, product_code=prod['product_code'], product_name=prod['product_name'], product_price=prod['product_price'], pub_date=timezone.now())
                p.save()
        return categories
    result_list = save_xlrd_sheet_to_db(sheet)
    template = loader.get_template('catalog/upload.html')
    context = {'result_list': result_list}
    return HttpResponse(template.render(context, request)) # return render(request, 'catalog/index.html', context)

def uploadcsv(request):
    # form = UploadFileForm(request.POST, request.FILES)
    # if form.is_valid():
    mylib.save_img('only_media', request.FILES['avatar2'],  request.POST['product_id'])
    next = request.POST.get('next', '/')
    return HttpResponseRedirect(next) # return HttpResponse("Изображение загружено успешно!")
    #return HttpResponse("Ошибка: изображение не загружено")



def update(request):
    import pandas as pd
    import numpy as np
    from sklearn.svm import LinearSVC
    from sklearn.model_selection import cross_val_score
    from sklearn.model_selection import train_test_split
    from sklearn.feature_extraction.text import TfidfVectorizer
    from nltk.corpus import stopwords
    import pickle
    import nltk
    nltk.download('stopwords')
    stopWords = stopwords.words('russian')
    #adress = settings.MEDIA_ROOT + '/products/'+ mylib.get_filename_by_partname(filenames, product.product_code)
    adress = settings.STATIC_ROOT + '/hello/'
    df = pd.read_csv(adress + 'models_dump/class_names.csv', encoding='utf-8') #df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    example = 'Когда движешься по Солотчинскому шоссе, в сторону Солотчи, на указателе мозолит глаз и сбивает водителя ванадльный иероглиф.'




    def predict(text):
        predictions = {}
        for target in ['theme', 'executor', 'category']:
            tfidf = pickle.load( open( adress + "models_dump/vectorizer.pkl", "rb" ) )
            model = pickle.load( open( adress + "models_dump/classifiers/clf_"+target+".pkl", "rb" ) )
            features = tfidf.transform(pd.Series(text)).toarray() # fit_transform will reduce features count, use ONLY transform
            target_id = model.predict(features)[0] #print(features.shape)
            target_name = df.loc[df[target+'_id']==target_id,target].iloc[0]
            predictions[target] = target_name

            filepath = settings.MEDIA_ROOT + '/products/'+ 'test' + '.csv'
            df2 = pd.read_csv(filepath, encoding='utf-8') #df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
            predictions = str(df2.head(1))

        return predictions


    import json
    response = HttpResponse(json.dumps({'product_values_count': predict(example), 'prediction':predict(request.POST['text_for_prediction'])}))
    return response


# Create your views here.
def index2(request):
    import pickle
    import pathlib
    import time
    import tqdm
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import os,sys,inspect,pickle,json,time,datetime,re
    import random as rn
    import lightgbm as lgb

    context = {'predictions': 'no','df': 'no','pred': 'no'}

    filepath = settings.MEDIA_ROOT + '/products/'+ 'train' + '.csv'
    #df2 = pd.read_csv(filepath, encoding='utf-8') #df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    df2 = pd.read_csv(filepath, parse_dates=["date"], index_col="date") #df = pd.read_json('NashDomRyazan-29-03-2019.json', encoding='utf-8')
    

    context['df'] = str(df2.head(1))
            
    adress = settings.STATIC_ROOT + '/hello/'

    # model = pickle.load( open( adress + "models_dump/model3_s8_2847.pkl", "rb" ) )
    model = pickle.load( open( adress + "models_dump/model3_s8_2847_model.pkl", "rb" ) )


    # y_train_pred_web = mylib_feateng.convert_to_input_predict(df2.head(1000), model)
    y_train_pred_web = mylib_feateng.convert_to_input_predict(df2, model)

    

    context['pred'] = y_train_pred_web
    # context['pred'] = model.predict(np.random.rand(1,880))
    #context['pred'] = model.predict(features)

    # return HttpResponse('Hello from Python!')
    return render(request, "index.html", context)




# def index(request):
#     r = requests.get('http://httpbin.org/status/418')
#     print(r.text)
#     return HttpResponse('<pre>' + r.text + '</pre>')

def db(request):

    greeting = Greeting()
    greeting.save()

    greetings = Greeting.objects.all()

    return render(request, "db.html", {"greetings": greetings})


