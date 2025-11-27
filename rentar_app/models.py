from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class Uzytkownik(models.Model):
    ROLA_CHOICES = [
        ('klient', 'Klient'),
        ('pracownik', 'Pracownik'),
        ('admin', 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rola = models.CharField(max_length=20, choices=ROLA_CHOICES, default='klient')
    kod_uzytkownika = models.CharField(max_length=50, unique=True, editable=False)
    data_utworzenia = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.kod_uzytkownika:
            num = 1
            while Uzytkownik.objects.filter(kod_uzytkownika=f"U{num:05d}").exists():
                num += 1
            self.kod_uzytkownika = f"U{num:05d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.rola})"


class Samochod(models.Model):
    STATUS_CHOICES = [
        ('dostepny', 'Dostępny'),
        ('niedostepny', 'Niedostępny'),
    ]

    SKRZYNIA_CHOICES = [
        ('manualna', 'Manualna'),
        ('automatyczna', 'Automatyczna'),
    ]

    NAPED_CHOICES = [
        ('rwd', 'RWD'),
        ('awd', 'AWD'),
        ('fwd', 'FWD'),
    ]

    nazwa = models.CharField(max_length=100)
    rocznik = models.IntegerField()
    pojemnosc_silnika = models.CharField(max_length=50)
    moc = models.IntegerField()
    przyspieszenie = models.CharField(max_length=50)
    predkosc_maksymalna = models.IntegerField()
    skrzynia_biegow = models.CharField(max_length=20, choices=SKRZYNIA_CHOICES)
    liczba_miejsc = models.IntegerField()
    naped = models.CharField(max_length=10, choices=NAPED_CHOICES)
    cena_za_dobe = models.DecimalField(max_digits=8, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='dostepny')
    kod_samochodu = models.CharField(max_length=50, unique=True, editable=False)
    zdjecie = models.ImageField(upload_to='samochody/', null=True, blank=True)
    data_utworzenia = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.kod_samochodu:
            num = 1
            while Samochod.objects.filter(kod_samochodu=f"S{num:05d}").exists():
                num += 1
            self.kod_samochodu = f"S{num:05d}"

        if self.moc < 0 or self.cena_za_dobe < 0 or self.liczba_miejsc < 0 or self.predkosc_maksymalna < 0:
            raise ValueError("Wartości nie mogą być ujemne")

        super().save(*args, **kwargs)

    def ma_aktywna_rezerwacje(self):
        return Rezerwacja.objects.filter(
            samochod=self,
            status__in=['oczekujacy', 'potwierdzony']
        ).exists()

    def __str__(self):
        return f"{self.nazwa} ({self.rocznik})"


class Rezerwacja(models.Model):
    STATUS_CHOICES = [
        ('oczekujacy', 'Oczekujący'),
        ('potwierdzony', 'Potwierdzony'),
        ('zakonczony', 'Zakończony'),
        ('anulowany', 'Anulowany'),
    ]

    klient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rezerwacje_klient')
    imie_klienta = models.CharField(max_length=100, blank=True)
    nazwisko_klienta = models.CharField(max_length=100, blank=True)
    samochod = models.ForeignKey(Samochod, on_delete=models.CASCADE, related_name='rezerwacje')
    data_odbioru = models.DateTimeField()
    data_zwrotu = models.DateTimeField()
    miejsce_odbioru = models.CharField(max_length=200)
    miejsce_zwrotu = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='oczekujacy')
    pracownik_potwierdzajacy = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                                 related_name='rezerwacje_potwierdzone')
    data_utworzenia = models.DateTimeField(auto_now_add=True)
    data_modyfikacji = models.DateTimeField(auto_now=True)
    kod_rezerwacji = models.CharField(max_length=50, unique=True, editable=False)
    kwota_razem = models.DecimalField(max_digits=8, decimal_places=2, default=0)

    def save(self, *args, **kwargs):
        if not self.kod_rezerwacji:
            num = 1
            while Rezerwacja.objects.filter(kod_rezerwacji=f"R{num:07d}").exists():
                num += 1
            self.kod_rezerwacji = f"R{num:07d}"

        if self.data_zwrotu <= self.data_odbioru:
            raise ValueError("Data zwrotu musi być po dacie odbioru")

        if not self.imie_klienta or not self.nazwisko_klienta:
            self.imie_klienta = self.klient.first_name
            self.nazwisko_klienta = self.klient.last_name

        dni = (self.data_zwrotu - self.data_odbioru).days
        if dni == 0:
            dni = 1

        self.kwota_razem = self.samochod.cena_za_dobe * dni

        if self.data_zwrotu <= timezone.now() and self.status != 'zakonczony':
            self.status = 'zakonczony'

        super().save(*args, **kwargs)

    def liczba_dni(self):
        dni = (self.data_zwrotu - self.data_odbioru).days
        return dni if dni > 0 else 1

    def __str__(self):
        return f"Rezerwacja {self.kod_rezerwacji} - {self.samochod.nazwa}"
