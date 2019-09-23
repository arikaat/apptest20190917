#アプリ側のurl.py
from django.urls import path
from . import views
from django.urls import include, path

app_name = 'accounts'

urlpatterns = [
    path('accounts/', include('django.contrib.auth.urls')), #  このアプリ全体の親アドレス
    #以下は子アドレス
    
    #テスト用20190922
    path('convert/', views.Convert.as_view(), name='convert'),


    #Top page 
    path('', views.Top.as_view(), name='top'),          #accounts:top = accounts/top.html
    #ログインとログアウト関連
    path('login/', views.Login.as_view(), name='login'),    #accounts:login = accounts/login.html
    path('logout/', views.Logout.as_view(), name='logout'), #accounts:logout = ログアウト後のジャンプ先htmlへ
    
    # 本会員登録ページ
    path('user_create/', views.UserCreate.as_view(), name='user_create'),
    path('user_create/done', views.UserCreateDone.as_view(), name='user_create_done'),
    path('user_create/complete/<token>/', views.UserCreateComplete.as_view(), name='user_create_complete'),

    #mypage
    path('user_detail/<int:pk>/', views.UserDetail.as_view(), name='user_detail'),
    path('user_update/<int:pk>/', views.UserUpdate.as_view(), name='user_update'),

    #password change
    path('password_change/', views.PasswordChange.as_view(), name='password_change'),
    path('password_change/done/', views.PasswordChangeDone.as_view(), name='password_change_done'),

    #password reset
    path('password_reset/', views.PasswordReset.as_view(), name='password_reset'),
    path('password_reset/done/', views.PasswordResetDone.as_view(), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/', views.PasswordResetConfirm.as_view(), name='password_reset_confirm'),
    path('password_reset/complete/', views.PasswordResetComplete.as_view(), name='password_reset_complete'),

    #email address change
    path('email/change/', views.EmailChange.as_view(), name='email_change'),
    path('email/change/done/', views.EmailChangeDone.as_view(), name='email_change_done'),
    path('email/change/complete/<str:token>/', views.EmailChangeComplete.as_view(), name='email_change_complete'),
    
    #Administrator level 
    #User_List
    path('alskdjfhga/mznxbcvm/user_admin_list', views.UserAdminList.as_view(), name='user_admin_list'),

   

]