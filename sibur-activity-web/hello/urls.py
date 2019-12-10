from django.urls import include, path
from . import views
app_name = 'hello'
urlpatterns = [
    path('', views.index, name='index'), # ex: /about/
    path('atc_index', views.atc_index, name='atc_index'), # ex: /about/
    path('update/', views.update, name='update'), # ex: /about/
    path('atc_update/', views.atc_update, name='atc_update'), # ex: /about/
    path('uploadcsv/', views.uploadcsv, name='uploadcsv'), # ex: /about/
]

