from django.contrib import admin
from .forms import ConvertForm
from .models import DataFile

#adminサイトに登録するDataFile編集フォーム
class ConverterAdmin(admin.ModelAdmin):
    form = ConvertForm  #ConvertFormをformtemplateへ


admin.site.register(DataFile, ConverterAdmin)   #adminサイトにDataFileモデル登録。本アプリグループの場合、accountsアプリが主
