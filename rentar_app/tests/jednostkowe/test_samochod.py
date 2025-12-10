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


    def test_14_rezerwacja_oczekujaca_zwraca_true(self):
        """TEST 14: Rezerwacja 'oczekujacy' powinna zwrócić True"""
        Rezerwacja.objects.create(
            samochod=self.samochod,
            uzytkownik_id=self.user.id,
            data_poczatku=self.dzisiaj,
            data_konca=self.dzisiaj + timedelta(days=1),
            status='oczekujacy'
        )

        wynik = self.samochod.ma_aktywna_rezerwacje()
        self.assertTrue(wynik)
        print("TEST 14 PASS: Rezerwacja 'oczekujacy' zwraca True")

    def test_15_rezerwacja_potwierdzona_zwraca_true(self):
        """TEST 15: Rezerwacja 'potwierdzony' powinna zwrócić True"""
        Rezerwacja.objects.create(
            samochod=self.samochod,
            uzytkownik_id=self.user.id,
            data_poczatku=self.dzisiaj,
            data_konca=self.dzisiaj + timedelta(days=2),
            status='potwierdzony'
        )

        wynik = self.samochod.ma_aktywna_rezerwacje()
        self.assertTrue(wynik)
        print("TEST 15 PASS: Rezerwacja 'potwierdzony' zwraca True")

    def test_16_rezerwacja_anulowana_zwraca_false(self):
        """TEST 16: Rezerwacja 'anulowany' powinna zwrócić False"""
        Rezerwacja.objects.create(
            samochod=self.samochod,
            uzytkownik_id=self.user.id,
            data_poczatku=self.dzisiaj,
            data_konca=self.dzisiaj + timedelta(days=1),
            status='anulowany'
        )

        wynik = self.samochod.ma_aktywna_rezerwacje()
        self.assertFalse(wynik)
        print("TEST 16 PASS: Rezerwacja 'anulowany' zwraca False")

    def test_17_rezerwacja_zakonczena_zwraca_false(self):
        """TEST 17: Rezerwacja 'zakonczony' powinna zwrócić False"""
        Rezerwacja.objects.create(
            samochod=self.samochod,
            uzytkownik_id=self.user.id,
            data_poczatku=self.dzisiaj - timedelta(days=2),
            data_konca=self.dzisiaj - timedelta(days=1),
            status='zakonczony'
        )

        wynik = self.samochod.ma_aktywna_rezerwacje()
        self.assertFalse(wynik)
        print("TEST 17 PASS: Rezerwacja 'zakonczony' zwraca False")

    def test_18_wiele_rezerwacji_z_aktywna(self):
        """TEST 18: Kilka rezerwacji, jedna aktywna - zwróć True"""
        # Rezerwacja anulowana
        Rezerwacja.objects.create(
            samochod=self.samochod,
            uzytkownik_id=self.user.id,
            data_poczatku=self.dzisiaj - timedelta(days=5),
            data_konca=self.dzisiaj - timedelta(days=3),
            status='anulowany'
        )

        # Rezerwacja aktywna
        Rezerwacja.objects.create(
            samochod=self.samochod,
            uzytkownik_id=self.user.id,
            data_poczatku=self.dzisiaj,
            data_konca=self.dzisiaj + timedelta(days=1),
            status='oczekujacy'
        )

        wynik = self.samochod.ma_aktywna_rezerwacje()
        self.assertTrue(wynik)
        print("TEST 18 PASS: Kilka rezerwacji, jedna aktywna - zwraca True")

    def test_19_wiele_rezerwacji_bez_aktywnych(self):
        """TEST 19: Kilka rezerwacji, żadna nie aktywna - zwróć False"""
        Rezerwacja.objects.create(
            samochod=self.samochod,
            uzytkownik_id=self.user.id,
            data_poczatku=self.dzisiaj - timedelta(days=3),
            data_konca=self.dzisiaj - timedelta(days=2),
            status='zakonczony'
        )

        Rezerwacja.objects.create(
            samochod=self.samochod,
            uzytkownik_id=self.user.id,
            data_poczatku=self.dzisiaj - timedelta(days=10),
            data_konca=self.dzisiaj - timedelta(days=9),
            status='anulowany'
        )

        wynik = self.samochod.ma_aktywna_rezerwacje()
        self.assertFalse(wynik)
        print("TEST 19 PASS: Kilka rezerwacji bez aktywnych - zwraca False")

    def test_20_inny_samochod_nie_wplywa(self):
        """TEST 20: Rezerwacje innego samochodu nie wpływają na wynik"""
        inny_samochod = Samochod.objects.create(
            nazwa='Audi A8',
            rocznik=2023,
            pojemnosc_silnika='3.0L',
            moc=460,
            przyspieszenie='3.8s',
            predkosc_maksymalna=250,
            skrzynia_biegow='automatyczna',
            liczba_miejsc=5,
            naped='fwd',
            cena_za_dobe=Decimal('350.00'),
            status='dostepny'
        )

        # Rezerwacja dla innego samochodu
        Rezerwacja.objects.create(
            samochod=inny_samochod,
            uzytkownik_id=self.user.id,
            data_poczatku=self.dzisiaj,
            data_konca=self.dzisiaj + timedelta(days=1),
            status='oczekujacy'
        )

        wynik = self.samochod.ma_aktywna_rezerwacje()
        self.assertFalse(wynik)
        print("TEST 20 PASS: Rezerwacje innego samochodu nie wpływają na wynik")
