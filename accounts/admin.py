#20190723　admin画面での挙動変更
#Model.pyで設定したCustomUserをadmin画面で設定できるようにする
#Emailアドレスを使用できるようにする
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.admin import GenericTabularInline
from .models import User, Company, Factory, Department, OfficialPosition, PhoneNumber

class MyUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = '__all__'

class MyUserCreationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email',)


class MyUserAdmin(UserAdmin):
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name','company', 'membershiplicense')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser',
                                       'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    form = MyUserChangeForm
    add_form = MyUserCreationForm
    list_display = ('email', 'first_name', 'last_name','Company_Name', 'Factory_Name', 'Department_Name', 'OfficialPosition_Name' ,'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('email', 'first_name', 'company__name') 
    ordering = ('email',)

    def Company_Name(self, obj):
        try:
            return obj.company.name
        except:
            return 'Notinhg'
    Company_Name.short_description = 'Company Name'

    def Factory_Name(self, obj):
        try:
            return obj.company.get_factory()
        except:
            return 'Notinhg'
    Factory_Name.short_description = 'Factory Name'

    def Department_Name(self, obj):
        try:
            return obj.company.get_department()
        except:
            return 'Notinhg'
    Department_Name.short_description = 'Department Name'

    def OfficialPosition_Name(self, obj):
        try:
            return obj.company.get_officialposition()
        except:
            return 'Notinhg'
    OfficialPosition_Name.short_description = 'OfficialPosition Name'

    def Phone_Number(self, obj):
        try:
            return obj.company.get_phonenumber()
        except:
            return 'Notinhg'
    Phone_Number.short_description = 'Phone Number'

   
class CompanyAdmin(admin.ModelAdmin):
    fields = ['name', 'factoryname', 'department', 'officialposition', 'phonenumber']

    list_display = ('name', 'factoryname', 'department', 'officialposition', 'phonenumber')


admin.site.register(User, MyUserAdmin)
admin.site.register(Company, CompanyAdmin)
admin.site.register(Factory)
admin.site.register(Department)
admin.site.register(OfficialPosition)
admin.site.register(PhoneNumber)