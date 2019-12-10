# from catalog.models import Category, Product
# from about.models import Parameter
from django.utils import timezone
import os
from django.conf import settings
import pdb #pdb.set_trace()
from django.http import HttpResponse
# from django.core.cache import cache # This is the memcache cache.
from django.core.cache import cache # This is the memcache cache.

def test(): return 8

def read_xlslines_as_files_and_folders(sheet): # separate by: value in 1 col, order and outline level (group)

    # config
    categories = []
    products = []
    # bookkeeping
    last_category = Category()
    path = []
    last_level_cat = -1;
    # last_level_prod = -1;
    # prepare data

    firstline = 10
    parameters = Parameter.objects.filter(key='firstline')
    if parameters:
        firstline = int(parameters.first().value)

    for i in range(firstline, sheet.nrows):
        # if i > 871: pdb.set_trace()
        if (sheet.row(i)[1].value==''):
            # change current path
            level = sheet.rowinfo_map[i].outline_level
            if (level == 0):                            path.append(-1)                               # -1 means 'no parent', root folder outline = 0
            elif (level > last_level_cat):              path.append(categories.index(last_category))  # last_cat is our parent, enter folder
            elif (level < last_level_cat):  
                for j in range(last_level_cat - level): path.pop() # back 1 or many times
            last_level_cat = level
            # save
            category = {'id' : 0, 'products' : [], 'category_name' : sheet.row(i)[2].value, 'parent_category_id' : path[-1], 'pub_date' : timezone.now()}
            categories.append(category)
            last_category = category
        else:
            prod_level = sheet.rowinfo_map[i].outline_level
            diff = prod_level - last_level_cat # if product level = cat level, means product is outside this cat
            if diff < 0: 
                index = categories.index(last_category) # product is inside last category
            else:
                index = path[diff - 1] # if diff =0, we get last element from diff (only parents are saved to path, i.e. last_category is not there)
            product = {'product_code' : "%05d" % sheet.row(i)[1].value, 'product_name' : sheet.row(i)[2].value, 'product_price' : "{0:.2f}".format(sheet.row(i)[3].value), 'pub_date' : timezone.now()}
            categories[index]['products'].append(product)
    return categories

# def xls_request_to_df(input_file): # example: df = xlsrequest_to_df(request.FILES['avatar'])
#     BytesIO = pd.io.common.BytesIO
#     df = pd.read_excel(BytesIO(input_file.read()), engine='xlrd')
#     return df

def custom_timestamp(): # 2019_04m_04d_01h_04m_04s_077859
    import datetime, re
    currentDT = datetime.datetime.now()
    regex = re.compile(r'^(.*)-(.*)-(.*) (.*):(.*):(.*)\.(.*)$', re.IGNORECASE)
    timestamp = regex.sub(r'\1_\2m_\3d_\4h_\5m_\6s_\7',str(currentDT))
    # print(timestamp)                                              # 2019_04m_04d_01h_04m_04s_077859
    # print (str(currentDT))                                        # 2019-04-04 01:04:04.077859
    return timestamp

def save_img(storage_type, uploaded_file, product_id): # without DB

    fname = 'train'
    # if storage_type == "only_media":
    # filepath = settings.MEDIA_ROOT + '/products/'+ product.product_code + '.jpg'
    filepath = settings.MEDIA_ROOT + '/products/'+ fname + '.csv'
    if os.path.isfile(filepath): os.remove(filepath) # I use 'pip install django-cleanup'
    # uploaded_file.name = product.product_code + '.jpg'
    uploaded_file.name = fname + '.csv'

    # product = Product.objects.get(id=product_id)
    # delete old
    filenames = os.listdir(settings.MEDIA_ROOT + '/products/')   
    # if list_contains_string(filenames, product.product_code): 
    if list_contains_string(filenames, fname): 
        # os.remove(settings.MEDIA_ROOT + '/products/'+ get_filename_by_partname(filenames, product.product_code))
        os.remove(settings.MEDIA_ROOT + '/products/'+ get_filename_by_partname(filenames, fname))
    # save big way 1:
    from django.core.files.storage import FileSystemStorage # https://stackoverflow.com/questions/26274021/simply-save-file-to-folder-in-django
    # new_name = product.product_code + '_' + custom_timestamp() + '.csv'
    new_name = fname + '.csv'
    FileSystemStorage(location=settings.MEDIA_ROOT + '/products').save(new_name, uploaded_file) # or use manual path: location='skladmax/media/products'
    # resize keeping aspect and compress:
    # import sys
    # from PIL import Image
    # basewidth = 1280
    # img_path = settings.MEDIA_ROOT + '/products/' + new_name
    # img = Image.open(img_path)
    # wpercent = (basewidth/float(img.size[0]))
    # hsize = int((float(img.size[1])*float(wpercent)))
    # img = img.resize((basewidth,hsize), Image.ANTIALIAS)
    # img.save(img_path, format='JPEG', quality=50) # works even with non jpeg
    cache.clear() # fixes error: changed img not updated, but peaking from cache




def save_img_old(storage_type, uploaded_file, product_id): # without DB
    if storage_type == "database_and_media":
        # must have column - "product_photo = models.ImageField(upload_to='products', default=settings.MEDIA_ROOT + settings.MEDIA_DEFAULT_IMG)"
        # link in html: {{MEDIA_URL}}{{product.product_photo}}
        product = Product.objects.get(id=product_id)
        # filepath = settings.MEDIA_ROOT + '\\products\\' + product.product_code + '.jpg'
        filepath = settings.MEDIA_ROOT + '/products/'+ product.product_code + '.jpg'
        if os.path.isfile(filepath): os.remove(filepath) # I use 'pip install django-cleanup'
        # cache.clear() # fixes error: changed img not updated, but peaking from cache
        uploaded_file.name = product.product_code + '.jpg'
        product.product_photo = uploaded_file
        product.save()
    # elif storage_type == "only_media": # not working for 07315_sdfoj0923.jpg
    #     product = Product.objects.get(id=product_id)
    #     # delete old
    #     filepath = settings.MEDIA_ROOT + '/products/'+ product.product_code + '.jpg'
    #     if os.path.isfile(filepath): os.remove(filepath) # I use 'pip install django-cleanup'
    #     # save big way 1:
    #     from django.core.files.storage import FileSystemStorage # https://stackoverflow.com/questions/26274021/simply-save-file-to-folder-in-django
    #     FileSystemStorage(location=settings.MEDIA_ROOT + '/products').save(product.product_code+'.jpg', uploaded_file) # or use manual path: location='skladmax/media/products'
    elif storage_type == "only_media": # working for 07315_sdfoj0923.jpg
        product = Product.objects.get(id=product_id)
        # delete old
        filenames = os.listdir(settings.MEDIA_ROOT + '/products/')   
        if list_contains_string(filenames, product.product_code): 
            os.remove(settings.MEDIA_ROOT + '/products/'+ get_filename_by_partname(filenames, product.product_code))
        # save big way 1:
        from django.core.files.storage import FileSystemStorage # https://stackoverflow.com/questions/26274021/simply-save-file-to-folder-in-django
        new_name = product.product_code + '_' + custom_timestamp() + '.jpg'
        FileSystemStorage(location=settings.MEDIA_ROOT + '/products').save(new_name, uploaded_file) # or use manual path: location='skladmax/media/products'
        # resize keeping aspect and compress:
        import sys
        from PIL import Image
        basewidth = 1280
        img_path = settings.MEDIA_ROOT + '/products/' + new_name
        img = Image.open(img_path)
        wpercent = (basewidth/float(img.size[0]))
        hsize = int((float(img.size[1])*float(wpercent)))
        img = img.resize((basewidth,hsize), Image.ANTIALIAS)
        img.save(img_path, format='JPEG', quality=50) # works even with non jpeg

        # save mini img way 1:
        # from PIL import Image # pip install Pillow python-resize-image
        # from resizeimage import resizeimage
        # img_path = settings.MEDIA_ROOT + '\\products\\' + product.product_code
        # with open(img_path + '.jpg', 'r+b') as f:
        #     with Image.open(f) as image:
        #         cover = resizeimage.resize_cover(image, [200, 100])
        #         cover.save(img_path + '_mini.jpg', image.format)

        # save mini img way 2:
        # import sys
        # from PIL import Image
        # size = 128, 128
        # img_path = settings.MEDIA_ROOT + '\\products\\' + product.product_code
        # with open(img_path + '.jpg', 'r+b') as f:
        #     im = Image.open(f)
        #     im.thumbnail(size, Image.ANTIALIAS)
        #     im.save(img_path + '_mini.jpg', "JPEG")

        # save big new way 2:
        # from django.core.files.storage import default_storage # If you use default_storage, in the future if you want to use aws, azure etc as file store with multiple Django worker your code will work without any change.
        # default_storage.save('products/'+product.product_code+'.jpg', uploaded_file)
        cache.clear() # fixes error: changed img not updated, but peaking from cache



def get_all_parents(current_category):
    path = []
    if current_category != None:
        last_category = current_category
        while last_category.parent_category_id != 0:
            last_category = Category.objects.get(id=last_category.parent_category_id)
            path.insert(0,last_category)
    return path

def generate_workbook_xls(request, categories, price_date):
    import xlwt # https://github.com/python-excel/xlwt
    from datetime import datetime
    # style0 = xlwt.easyxf('font: name Times New Roman, color-index black, bold off', num_format_str='#,##0.00')
    style_cat = xlwt.easyxf('font: name Arial, color-index black, bold on, height 180; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color gray25;')
    style_cat_link = xlwt.easyxf('font: name Arial, color-index black, bold off, height 180; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color gray25; align: horiz center')
    style_prod = xlwt.easyxf('font: name Arial, color-index black, bold off, height 160; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')
    style_prod_price = xlwt.easyxf('font: name Arial, color-index black, bold off, height 160; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;', num_format_str='0.00')
    style_prod_code = xlwt.easyxf('font: name Arial, color-index black, bold off, height 160; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;', num_format_str='00000')
    style_prod_link = xlwt.easyxf('font: name Arial, color-index black, bold off, height 160; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white; align: horiz center')
    # style1_date = xlwt.easyxf(num_format_str='D-MMM-YY')
    wb = xlwt.Workbook()
    ws = wb.add_sheet('Sheet_1')

    ws.col(0).width = 1 * 256
    ws.col(1).width = 7 * 256
    ws.col(2).width = 51 * 256
    ws.col(3).width = 16 * 256
    ws.col(4).width = 16 * 256

    ws.write(0, 1, 'Прайс-лист', xlwt.easyxf('font: name Arial, color-index black, bold on, height 720')); ws.row(0).height = 50*20; ws.row(0).height_mismatch = True
    ws.write(2, 1, 'Плаксин Максим Алексеевич', xlwt.easyxf('font: name Arial, color-index black, bold on, height 280')); ws.row(2).height = 14*20; ws.row(2).height_mismatch = True
    ws.write(4, 1, 'В валютах цен.', xlwt.easyxf('font: name Arial, color-index black, bold off, height 160')); ws.row(4).height = 10*20; ws.row(4).height_mismatch = True
    ws.write(5, 1, 'Цены указаны на ' + price_date, xlwt.easyxf('font: name Arial, color-index black, bold off, height 160')); ws.row(5).height = 10*20; ws.row(5).height_mismatch = True
    ws.write(9, 1, 'Код', xlwt.easyxf('font: name Arial, color-index black, bold on, height 180; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')); ws.row(9).height = 18*20; ws.row(9).height_mismatch = True
    ws.write(9, 2, 'Номенклатура', xlwt.easyxf('font: name Arial, color-index black, bold on, height 180; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')); ws.row(9).height = 18*20; ws.row(9).height_mismatch = True
    ws.write(9, 3, 'Опт штучно', xlwt.easyxf('font: name Arial, color-index black, bold on, height 180; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')); ws.row(9).height = 18*20; ws.row(9).height_mismatch = True
    ws.write(9, 4, 'Ссылка на сайт', xlwt.easyxf('font: name Arial, color-index black, bold on, height 180; borders: left thin, right thin, top thin, bottom thin; pattern: pattern solid, fore_color white;')); ws.row(9).height = 18*20; ws.row(9).height_mismatch = True
    

    last_level = 0
    i = 10
    for cat in categories:
        ws.write(i, 1, '', style_cat);
        ws.write(i, 2, cat.category_name, style_cat); ws.row(i).height = 12*20; ws.row(i).height_mismatch = True
        ws.write(i, 3, '', style_cat);
        click = "{0}{1}/catalog/{2}".format('https://', request.get_host(), cat.id)
        # ws.write(i, 4, xlwt.Formula('HYPERLINK("{0}";"{1}")'.format(click, str(cat.category_name).replace('"', '""'))), style_cat)
        ws.write(i, 4, xlwt.Formula('HYPERLINK("{0}";"{1}")'.format(click, 'click')), style_cat_link)


        last_level = len(get_all_parents(cat))
        ws.row(i).level = last_level


        i += 1
        for prod in cat.product_set.all().order_by('-id').reverse():
            # ws.write(i, 1, "%05d" % int(prod.product_code), style_prod_code); ws.row(i).height = 12*20; ws.row(i).height_mismatch = True
            ws.write(i, 1, int(prod.product_code), style_prod_code); ws.row(i).height = 12*20; ws.row(i).height_mismatch = True
            click = "{0}{1}/product/{2}".format('https://', request.get_host(), prod.id)
            # ws.write(i, 2, xlwt.Formula('HYPERLINK("{0}";"{1}")'.format(click, str(prod.product_name).replace('"', '""'))), style_prod)
            ws.write(i, 2, prod.product_name, style_prod)
            ws.write(i, 3, prod.product_price, style_prod_price)
            ws.write(i, 4, xlwt.Formula('HYPERLINK("{0}";"{1}")'.format(click, 'click')), style_prod_link)
            ws.row(i).level = last_level + 1
            i += 1
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="price.xls"'
    wb.save(response)
    return response







def convert_date(x,y,z):
    import datetime
    orig_date = datetime.datetime(x,y,z)
    orig_date = str(orig_date)
    d = datetime.datetime.strptime(orig_date, '%Y-%m-%d %H:%M:%S')
    d = d.strftime('%d.%m.%y')
    return d    

def list_contains_string(strings_list, string_part):  # '07263' -> True
    for f in strings_list:
        if f[0:5] == string_part: return True
    return False

def get_filename_by_partname(strings_list, string_part):  # '07263' -> '07315_912321097.jpg'
    for f in strings_list:
        # print(f)
        if f[0:5] == string_part: return f
    return None

def assign_imgs_to_products(products, product_page):
    # if not product_page:
    images = {}
    for p in products:

        # code = '07315'
        filenames =os.listdir(settings.MEDIA_ROOT + '/products/')   
        # list_contains_string(filenames, p.product_code)
            

        # if os.path.isfile(settings.MEDIA_ROOT + '/products/'+ p.product_code + '.jpg'): # not working when name='07315_01fds.jpg'
            # images[p.id] = settings.MEDIA_URL + 'products/' + p.product_code + '.jpg'
        if list_contains_string(filenames, p.product_code): 
            images[p.id] = settings.MEDIA_URL + 'products/' + get_filename_by_partname(filenames, p.product_code)
        else:                        
            images[p.id] = settings.MEDIA_URL + 'products/' + 'no_image' + '.jpg'
    return images
    # filepath = settings.MEDIA_ROOT + '\\products\\' + p.product_code + '.jpg'
    # # if os.path.isfile(filepath): images[p.id] = settings.MEDIA_URL + "products/" + p.product_code + ".jpg"
    # if os.path.isfile(filepath): images[p.id] = p.product_code + '.jpg'
    # # else:                        images[p.id] = settings.MEDIA_URL + "products"  + settings.MEDIA_DEFAULT_IMG
    # else:                        images[p.id] = settings.MEDIA_DEFAULT_IMG
        

# def assign_imgs_to_products(products, product_page): # special for image_fit version
#     if not product_page:
#         images = {}
#         for p in products:
#             filepath = settings.MEDIA_ROOT + '/products/' + p.product_code + '.jpg'
#             if os.path.isfile(filepath): images[p.id] = p.product_code + ".jpg"
#             else:                        images[p.id] = settings.MEDIA_DEFAULT_IMG
#         return images
#     else:
#         images = {}
#         for p in products:
#             if os.path.isfile(settings.MEDIA_ROOT + '/products/'+ p.product_code + '.jpg'): 
#                 images[p.id] = settings.MEDIA_URL + 'products/' + p.product_code + '.jpg'
#             else:                        
#                 images[p.id] = settings.MEDIA_URL + 'products/' + 'no_image' + '.jpg'
#         return images




def reset_autoincrement(model1, model2):
    from django.core.management.color import no_style
    from django.db import connection
    sequence_sql = connection.ops.sequence_reset_sql(no_style(), [model1, model2])
    with connection.cursor() as cursor:
        for sql in sequence_sql:
            cursor.execute(sql)

def divide_files_on_batches(folder, filenames, size_limit_mb):
        batches = []
        mini_batch = []
        sum_size_mb = 0
        for filename in filenames:
            mini_batch.append(filename)
            fpath = folder + filename
            sum_size_mb += os.stat(fpath).st_size/(1024*1024)
            if sum_size_mb > size_limit_mb:
                batches.append({'files_list': mini_batch, 'files_size_mb':round(sum_size_mb,2)})
                sum_size_mb = 0
                mini_batch = []
        batches.append({'files_list': mini_batch, 'files_size_mb':round(sum_size_mb,2)})
        return batches
#batches = divide_files_on_batches(folder, filenames, SIZE_LIMIT_MB) #print(batches)
   

def getfiles(request, batch_number):
    JUPYTER = False
    SIZE_LIMIT_MB = 200
    
    import os
    import zipfile # from io import StringIO
    from io import BytesIO
    from django.http import HttpResponse
    import datetime
    from django.utils import dateformat
    # Files (local path) to put in the .zip
    # FIXME: Change this (get paths from DB etc)
    if JUPYTER: folder='test_imgs/' + 'products/'
    else: folder=settings.MAIN_APP + settings.MEDIA_URL + 'products/'  # insert the path to your directory   

    filenames =os.listdir(folder)   
    # filenames = [settings.MAIN_APP + settings.MEDIA_URL + 'products/07316.jpg'] # only concrete file
    # filenames = ["skladmax/media/products/01290.jpg", "skladmax/media/products/00061.jpg"] # only local
    # Folder name in ZIP archive which contains the above files
    # E.g [thearchive.zip]/somefiles/file2.txt
    # FIXME: Set this to something better

    # Open StringIO to grab in-memory ZIP contents
    # s = StringIO.StringIO()
    s = BytesIO()
    # The zip compressor
    zf = zipfile.ZipFile(s, "w")
    
    batches = divide_files_on_batches(folder, filenames, SIZE_LIMIT_MB) #print(batches)
    
    if JUPYTER: zip_subdir = "all_images_skladmax_"
    else: zip_subdir = "all_images_skladmax_" + dateformat.format(datetime.datetime.now(), 'F_j_Y') + '_part_' + str(batch_number+1) + '_of_' + str(len(batches))
    zip_filename = "%s.zip" % zip_subdir
    
    for filename in batches[batch_number]['files_list']:
        fpath = folder + filename
        # Calculate path for file in zip
        fdir, fname = os.path.split(fpath)
        zip_path = os.path.join(zip_subdir, fname)
        # Add file, at correct path
        zf.write(fpath, zip_path)
    # Must close zip for all contents to be written
    zf.close()
    # Grab ZIP file from in-memory, make response with correct MIME-type
    # resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
    resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
    # ..and correct content-disposition
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp  
#getfiles('request',0)


# def getfiles(request):
#     import os
#     import zipfile
#     # from io import StringIO
#     from io import BytesIO
#     from django.http import HttpResponse
#     import datetime
#     from django.utils import dateformat
#     # Files (local path) to put in the .zip
#     # FIXME: Change this (get paths from DB etc)
#     folder=settings.MAIN_APP + settings.MEDIA_URL + 'products/'  # insert the path to your directory   
#     filenames =os.listdir(folder)   
#     # filenames = [settings.MAIN_APP + settings.MEDIA_URL + 'products/07316.jpg'] # only concrete file
#     # filenames = ["skladmax/media/products/01290.jpg", "skladmax/media/products/00061.jpg"] # only local
#     # Folder name in ZIP archive which contains the above files
#     # E.g [thearchive.zip]/somefiles/file2.txt
#     # FIXME: Set this to something better
#     zip_subdir = "all_images_skladmax_" + dateformat.format(datetime.datetime.now(), 'F_j_Y')
#     zip_filename = "%s.zip" % zip_subdir
#     # Open StringIO to grab in-memory ZIP contents
#     # s = StringIO.StringIO()
#     s = BytesIO()
#     # The zip compressor
#     zf = zipfile.ZipFile(s, "w")
#     for fpath in filenames:
#         fpath = folder + fpath
#         # Calculate path for file in zip
#         fdir, fname = os.path.split(fpath)
#         zip_path = os.path.join(zip_subdir, fname)
#         # Add file, at correct path
#         zf.write(fpath, zip_path)
#     # Must close zip for all contents to be written
#     zf.close()
#     # Grab ZIP file from in-memory, make response with correct MIME-type
#     # resp = HttpResponse(s.getvalue(), mimetype = "application/x-zip-compressed")
#     resp = HttpResponse(s.getvalue(), content_type="application/x-zip-compressed")
#     # ..and correct content-disposition
#     resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
#     return resp   

