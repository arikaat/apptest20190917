#アプリ側のurl.py
from django.urls import path
from . import views
from django.urls import include, path
from django.contrib import admin

app_name = 'smtdataconverter'

urlpatterns = [
   
    path('smtdataconverter/', include('django.contrib.auth.urls')), #  追加
    #Top page 
    path('smtdataconverter_top', views.SmtDataConverterTop.as_view(), name='smtdataconverter_top'),
    path('smtdataconverter_top/upload/', views.upload, name='upload'),
    path('smtdataconverter_top/convertfile_list/', views.ConvertFileList.as_view(), name='convertfile_list'),
    path('smtdataconverter_top/convertResult/', views.ConvertResult.as_view(), name='smtdataconverter_convert_result'),

]
