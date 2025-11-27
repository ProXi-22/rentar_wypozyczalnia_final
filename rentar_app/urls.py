from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('cars/', views.cars_list, name='cars_list'),
    path('rezerwacja/<int:samochod_id>/', views.rezerwacja_samochodu, name='rezerwacja_samochodu'),
    path('moje-rezerwacje/', views.moje_rezerwacje, name='moje_rezerwacje'),
    path('anuluj-rezerwacje/<int:rezerwacja_id>/', views.anuluj_rezerwacje, name='anuluj_rezerwacje'),
    path('panel-pracownika/', views.panel_pracownika, name='panel_pracownika'),
    path('potwierdz-rezerwacje/<int:rezerwacja_id>/', views.potwierdz_rezerwacje, name='potwierdz_rezerwacje'),
    path('zarzadzanie-samochodami/', views.zarzadzanie_samochodami, name='zarzadzanie_samochodami'),
    path('dodaj-samochod/', views.dodaj_samochod, name='dodaj_samochod'),
    path('edytuj-samochod/<int:samochod_id>/', views.edytuj_samochod, name='edytuj_samochod'),
    path('usun-samochod/<int:samochod_id>/', views.usun_samochod, name='usun_samochod'),
    path('zarzadzanie-uzytkownikami/', views.zarzadzanie_uzytkownikami, name='zarzadzanie_uzytkownikami'),
    path('dodaj-pracownika/', views.dodaj_pracownika, name='dodaj_pracownika'),
    path('edytuj-pracownika/<int:uzytkownik_id>/', views.edytuj_pracownika, name='edytuj_pracownika'),
    path('usun-pracownika/<int:uzytkownik_id>/', views.usun_pracownika, name='usun_pracownika'),
    path('raporty/', views.raporty, name='raporty'),
]
