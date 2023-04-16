from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import MainView,ResultView,ReservationView,InformationView,\
    LoginView,LogoutView,HistoryView

urlpatterns = [
    path('',MainView.as_view(),name='main'),
    path('main/',MainView.as_view(),name='main'),
    path('result/<str:kensaku><int:index>/',ResultView.as_view(),name='result'),
    path('result/<str:kensaku>/',ResultView.as_view(),name='result'),
    path('reservation/<str:reservation>',ReservationView.as_view(),name='reservation'),
    path('information/',InformationView.as_view(),name='information'),
    path('history/<str:kensaku>/',HistoryView.as_view(),name='history'),
    path('login/',LoginView.as_view(),name='login'),
    path('logout/',LogoutView.as_view(),name='logout'),
]+static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)+\
    static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)