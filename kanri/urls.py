from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from kanri import views
from .views import RentView,ReservingView,CommentView,CreateView,DeleteView,UpdateView

urlpatterns = [
    path('rent/',RentView.as_view(),name='rent'),
    path('rent/<str:userid>/',RentView.as_view(),name='rent'),
    path('reserving/',ReservingView.as_view(),name='reserving'),
    path('comment/',CommentView.as_view(),name='comment'),
    path('create/',CreateView.as_view(),name='create'),
    path('update/<int:pk>',UpdateView.as_view(),name='update'),
    path('delete/',DeleteView.as_view(),name='delete'),
    path('delete/<int:pk>',DeleteView.as_view(),name='delete'),
]+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)+\
    static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)