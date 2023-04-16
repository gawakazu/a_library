from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from import_export.admin import ImportExportModelAdmin
from .models import BookModel,LibraryModel,CustomUser,ReservationModel,HistoryModel,PublisherModel,AuthorModel,CommentModel

class BookModelAdmin(ImportExportModelAdmin):
    list_display = ['id','book','book2','book3','publisher','year','author', 'library','number','images']

class LibraryModelAdmin(ImportExportModelAdmin):
    list_display = ['id','library','location','location_map']

class AuthorModelAdmin(ImportExportModelAdmin):
    list_display = ['id','author','author2']

class PublisherModelAdmin(ImportExportModelAdmin):
    list_display = ['id','publisher','publisher2']

class ReservationModelAdmin(ImportExportModelAdmin):
    list_display = ['id','book','user','reservation_date','start_date','end_date','limited_date','status']

class HistoryModelAdmin(ImportExportModelAdmin):
    list_display = ['id','book','user','start_day','end_day']

class CommentModelAdmin(ImportExportModelAdmin):
    list_display =['id','comment','status']

class CustomUserAdmin(UserAdmin,ImportExportModelAdmin):
    list_display = ['username','age','email','last_name','first_name','address','zip_code']
    empty_value_display = '-empty-'
    fieldsets = (
        (None,{'fields':('username','password')}),
        (_('Personal info'),{'fields':('first_name','last_name','email','age','address','zip_code')}),
        (_('Permissions'),{'fields':('is_active','is_staff','is_superuser','groups','user_permissions')}),
        (_('Important dates'),{'fields':('last_login','date_joined')}),
    )


admin.site.register(BookModel,BookModelAdmin)
admin.site.register(LibraryModel,LibraryModelAdmin)
admin.site.register(CustomUser,CustomUserAdmin)
admin.site.register(ReservationModel,ReservationModelAdmin)
admin.site.register(HistoryModel,HistoryModelAdmin)
admin.site.register(AuthorModel,AuthorModelAdmin)
admin.site.register(PublisherModel,PublisherModelAdmin)
admin.site.register(CommentModel,CommentModelAdmin)
