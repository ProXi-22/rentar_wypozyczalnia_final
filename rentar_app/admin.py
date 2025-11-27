from django.contrib import admin
from .models import Uzytkownik, Samochod, Rezerwacja

@admin.register(Uzytkownik)
class UzytkownikAdmin(admin.ModelAdmin):
    list_display = ['user', 'rola', 'kod_uzytkownika', 'data_utworzenia']
    list_filter = ['rola', 'data_utworzenia']
    search_fields = ['user__username', 'kod_uzytkownika']

@admin.register(Samochod)
class SamochodAdmin(admin.ModelAdmin):
    list_display = ['nazwa', 'rocznik', 'moc', 'cena_za_dobe', 'status', 'kod_samochodu']
    list_filter = ['status', 'rocznik', 'skrzynia_biegow']
    search_fields = ['nazwa', 'kod_samochodu']

@admin.register(Rezerwacja)
class RezerwacjaAdmin(admin.ModelAdmin):
    list_display = ['kod_rezerwacji', 'klient', 'samochod', 'data_odbioru', 'data_zwrotu', 'status', 'kwota_razem']
    list_filter = ['status', 'data_odbioru', 'data_utworzenia']
    search_fields = ['kod_rezerwacji', 'klient__username', 'samochod__nazwa']