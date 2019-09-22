#アプリ側のurl.py
from django.urls import path
from . import views
from django.urls import include, path

app_name = 'onlinetop'

urlpatterns = [
   
    path('', include('django.contrib.auth.urls')), #  追加
    #Top page 
    path('', views.OnlineTop.as_view(), name='online_top'),
    path('membership/top', views.MembershipTop.as_view(), name='membership_top'),
    
]