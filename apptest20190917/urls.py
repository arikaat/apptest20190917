"""apptest20190917 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
#元々の宣言部
#from django.contrib import admin
#from django.urls import path

#プロジェクト側のurls.py

from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static


#各アプリのパスをここに記載すること
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('accounts.urls')),      #20190723　ログイン画面表示
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

#下は元々の記述
#urlpatterns = [
#    path('admin/', admin.site.urls),
#]