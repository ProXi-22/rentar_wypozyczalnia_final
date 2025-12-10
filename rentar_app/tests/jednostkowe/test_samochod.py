from django.test import TestCase
from django.contrib.auth.models import User
from rentar_app.models import Samochod, Rezerwacja
from decimal import Decimal
from datetime import datetime, timedelta


class TestSamochodModel(TestCase):

    def setUp(self):
        self.samochod_data = {
            'nazwa': 'BMW M5',
            'rocznik': 2023,
            'pojemnosc_silnika': '4.4L',
            'moc': 625,
            'przyspieszenie': '3.1s',
            'predkosc_maksymalna': 305,
            'skrzynia_biegow': 'automatyczna',
            'liczba_miejsc': 5,
            'naped': 'rwd',
            'cena_za_dobe': Decimal('500.00'),
            'status': 'dostepny'
        }

        self.samochod = Samochod.objects.create(**self.samochod_data)

        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123',
            email='test@example.com'
        )

        self.dzisiaj = datetime.now().date()


    def test_01_generowanie_unikalnych_kodow(self):
        self.samochod_data['nazwa'] = 'Audi A8'
        samochod2 = Samochod.objects.create(**self.samochod_data)

        self.samochod_data['nazwa'] = 'Mercedes C63'
        samochod3 = Samochod.objects.create(**self.samochod_data)

        self.assertEqual(self.samochod.kod_samochodu, 'S00001')
        self.assertEqual(samochod2.kod_samochodu, 'S00002')
        self.assertEqual(samochod3.kod_samochodu, 'S00003')
        print("TEST 1 PASS: Kody auto-generowane: S00001, S00002, S00003")

    def test_02_nie_nadpisuje_custom_kodu(self):
        Samochod.objects.all().delete()
        samochod = Samochod(**self.samochod_data)
        samochod.kod_samochodu = 'CUSTOM_BMW'
        samochod.save()

        samochod.refresh_from_db()
        self.assertEqual(samochod.kod_samochodu, 'CUSTOM_BMW')
        print("TEST 2 PASS: Custom kod CUSTOM_BMW nie został nadpisany")

    def test_03_walidacja_ujemnej_mocy(self):
        self.samochod_data['moc'] = -100
        samochod = Samochod(**self.samochod_data)

        with self.assertRaises(ValueError) as context:
            samochod.save()

        self.assertIn("Wartości nie mogą być ujemne", str(context.exception))
        print("TEST 3 PASS: ValueError dla ujemnej mocy")

    def test_04_walidacja_ujemnej_ceny(self):
        self.samochod_data['cena_za_dobe'] = Decimal('-100.00')
        samochod = Samochod(**self.samochod_data)

        with self.assertRaises(ValueError):
            samochod.save()
        print("TEST 4 PASS: ValueError dla ujemnej ceny")

    def test_05_walidacja_ujemnej_liczby_miejsc(self):
        self.samochod_data['liczba_miejsc'] = -5
        samochod = Samochod(**self.samochod_data)

        with self.assertRaises(ValueError):
            samochod.save()
        print("TEST 5 PASS: ValueError dla ujemnej liczby miejsc")

    def test_06_walidacja_ujemnej_predkosci(self):
        self.samochod_data['predkosc_maksymalna'] = -250
        samochod = Samochod(**self.samochod_data)

        with self.assertRaises(ValueError):
            samochod.save()
        print("TEST 6 PASS: ValueError dla ujemnej prędkości")

