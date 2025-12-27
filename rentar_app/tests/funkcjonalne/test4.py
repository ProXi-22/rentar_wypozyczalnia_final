from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from rentar_app.models import Samochod, Rezerwacja, Uzytkownik
from decimal import Decimal
from datetime import timedelta


class TestRezerwacjaSamochoduAkceptacyjne(TestCase):

    def setUp(self):
        self.client = Client()

        self.samochod = Samochod.objects.create(
            nazwa='Audi RS6',
            rocznik=2023,
            pojemnosc_silnika='4.0L',
            moc=600,
            przyspieszenie='3.6s',
            predkosc_maksymalna=305,
            skrzynia_biegow='automatyczna',
            liczba_miejsc=5,
            naped='awd',
            cena_za_dobe=Decimal('1000.00'),
            status='dostepny'
        )

        self.user = User.objects.create_user(username='klient_test', password='password123')
        self.uzytkownik = Uzytkownik.objects.create(user=self.user, rola='klient')

    def test_01_klient_moze_dokonac_rezerwacji(self):

        self.client.login(username='klient_test', password='password123')

        data_start = timezone.now() + timedelta(days=1)
        data_koniec = data_start + timedelta(days=3)

        dane_rezerwacji = {
            'data_odbioru': data_start.strftime('%Y-%m-%dT%H:%M'),
            'data_zwrotu': data_koniec.strftime('%Y-%m-%dT%H:%M'),
            'miejsce_odbioru': 'Warszawa',
            'miejsce_zwrotu': 'Kraków'
        }

        url = reverse('rezerwacja_samochodu', args=[self.samochod.id])
        response = self.client.post(url, dane_rezerwacji)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('moje_rezerwacje'))

        rezerwacja = Rezerwacja.objects.first()
        self.assertIsNotNone(rezerwacja)
        self.assertEqual(rezerwacja.klient, self.user)
        self.assertEqual(rezerwacja.samochod, self.samochod)
        self.assertEqual(rezerwacja.status, 'oczekujacy')

        print("TEST 10.1 PASS: Klient pomyślnie utworzył rezerwację")

    def test_02_niezalogowany_nie_moze_rezerwowac(self):
        url = reverse('rezerwacja_samochodu', args=[self.samochod.id])
        response = self.client.get(url)

        self.assertRedirects(response, f'/login/?next={url}')
        print("TEST 10.1 PASS: Niezalogowany użytkownik przekierowany do logowania")