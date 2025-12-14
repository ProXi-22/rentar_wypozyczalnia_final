from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rentar_app.models import Samochod, Rezerwacja, Uzytkownik
from decimal import Decimal
from datetime import timedelta


class TestPotwierdzRezerwacjiAkceptacyjne(TestCase):

    def setUp(self):
        self.client = Client()
        self.samochod = Samochod.objects.create(
            nazwa='BMW M5',
            rocznik=2023,
            pojemnosc_silnika='4.4L',
            moc=625,
            przyspieszenie='3.1s',
            predkosc_maksymalna=305,
            skrzynia_biegow='automatyczna',
            liczba_miejsc=5,
            naped='rwd',
            cena_za_dobe=Decimal('500.00'),
            status='dostepny'
        )

        self.klient_user = User.objects.create_user(
            username='klient1',
            password='haslo123',
            email='klient@test.com',
            first_name='Jan',
            last_name='Kowalski'
        )
        self.klient = Uzytkownik.objects.create(
            user=self.klient_user,
            rola='klient'
        )

        self.pracownik_user = User.objects.create_user(
            username='pracownik1',
            password='haslo123',
            email='pracownik@test.com',
            first_name='Maria',
            last_name='Nowak'
        )
        self.pracownik = Uzytkownik.objects.create(
            user=self.pracownik_user,
            rola='pracownik'
        )

        self.admin_user = User.objects.create_user(
            username='admin1',
            password='haslo123',
            email='admin@test.com',
            first_name='Admin',
            last_name='System'
        )
        self.admin = Uzytkownik.objects.create(
            user=self.admin_user,
            rola='admin'
        )

        self.teraz = timezone.now()
        self.jutro = self.teraz + timedelta(days=1)
        self.pojutrze = self.teraz + timedelta(days=2)

        self.rezerwacja = Rezerwacja.objects.create(
            klient=self.klient_user,
            samochod=self.samochod,
            data_odbioru=self.teraz,
            data_zwrotu=self.pojutrze,
            miejsce_odbioru='Kraków',
            miejsce_zwrotu='Kraków',
            status='oczekujacy',
            imie_klienta='Jan',
            nazwisko_klienta='Kowalski'
        )

    def test_01_pracownik_moze_potwierdzi_rezerwacje(self):

        self.client.login(username='pracownik1', password='haslo123')

        url = reverse('potwierdz_rezerwacje', args=[self.rezerwacja.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)

        self.rezerwacja.refresh_from_db()
        self.assertEqual(self.rezerwacja.status, 'potwierdzony')

        self.assertEqual(self.rezerwacja.pracownik_potwierdzajacy, self.pracownik_user)

        print("TEST 1 PASS: Pracownik potwierdził rezerwację")


    def test_02_klient_nie_moze_potwierdzi_rezerwacje(self):
        self.client.login(username='klient1', password='haslo123')

        url = reverse('potwierdz_rezerwacje', args=[self.rezerwacja.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

        self.rezerwacja.refresh_from_db()
        self.assertEqual(self.rezerwacja.status, 'oczekujacy')

        print("TEST 2 PASS: Klient nie ma dostępu do potwierdzenia")

    def test_03_nie_mozna_potwierdzic_anulowanej(self):
        self.rezerwacja.status = 'anulowany'
        self.rezerwacja.save()

        self.client.login(username='pracownik1', password='haslo123')

        url = reverse('potwierdz_rezerwacje', args=[self.rezerwacja.id])
        response = self.client.get(url)

        self.rezerwacja.refresh_from_db()
        self.assertEqual(self.rezerwacja.status, 'anulowany')

        print("TEST 3 PASS: Nie można potwierdzić anulowanej rezerwacji")

    def test_04_nie_mozna_potwierdzi_zakonczonenej(self):
        self.rezerwacja.status = 'zakonczony'
        self.rezerwacja.save()

        self.client.login(username='pracownik1', password='haslo123')

        url = reverse('potwierdz_rezerwacje', args=[self.rezerwacja.id])
        response = self.client.get(url)

        self.rezerwacja.refresh_from_db()
        self.assertEqual(self.rezerwacja.status, 'zakonczony')

        print("TEST 4 PASS: Nie można potwierdzić zakończonej rezerwacji")
