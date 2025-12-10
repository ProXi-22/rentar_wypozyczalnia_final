from django.test import TestCase
from django.contrib.auth.models import User
from rentar_app.models import Samochod, Rezerwacja
from decimal import Decimal
from datetime import datetime, timedelta


class TestSamochodModel(TestCase):

    def setUp(self):
        """Przygotowanie danych testowych"""
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

    # ============ TESTY METODY SAVE() ============

    def test_01_generowanie_pierwszego_kodu(self):
        """TEST 1: Pierwsza instancja Samochodu powinna otrzymać kod S00001"""
        Samochod.objects.all().delete()
        samochod = Samochod.objects.create(**self.samochod_data)
        self.assertEqual(samochod.kod_samochodu, 'S00001')
        print("TEST 1 PASS: Kod samochodu S00001 wygenerowany poprawnie")

    def test_02_generowanie_unikalnych_kodow(self):
        """TEST 2: Kolejne samochody powinny mieć unikalne kody"""
        self.samochod_data['nazwa'] = 'Audi A8'
        samochod2 = Samochod.objects.create(**self.samochod_data)

        self.samochod_data['nazwa'] = 'Mercedes C63'
        samochod3 = Samochod.objects.create(**self.samochod_data)

        self.assertEqual(self.samochod.kod_samochodu, 'S00001')
        self.assertEqual(samochod2.kod_samochodu, 'S00002')
        self.assertEqual(samochod3.kod_samochodu, 'S00003')
        print("TEST 2 PASS: Kody auto-generowane: S00001, S00002, S00003")

    def test_03_nie_nadpisuje_custom_kodu(self):
        """TEST 3: Custom kod nie powinien być nadpisany"""
        Samochod.objects.all().delete()
        samochod = Samochod(**self.samochod_data)
        samochod.kod_samochodu = 'CUSTOM_BMW'
        samochod.save()

        samochod.refresh_from_db()
        self.assertEqual(samochod.kod_samochodu, 'CUSTOM_BMW')
        print("TEST 3 PASS: Custom kod CUSTOM_BMW nie został nadpisany")

    def test_04_walidacja_ujemnej_mocy(self):
        """TEST 4: Ujemna moc powinna wyrzucić ValueError"""
        self.samochod_data['moc'] = -100
        samochod = Samochod(**self.samochod_data)

        with self.assertRaises(ValueError) as context:
            samochod.save()

        self.assertIn("Wartości nie mogą być ujemne", str(context.exception))
        print("TEST 4 PASS: ValueError wyrzucony dla ujemnej mocy")

    def test_05_walidacja_ujemnej_ceny(self):
        """TEST 5: Ujemna cena powinna wyrzucić ValueError"""
        self.samochod_data['cena_za_dobe'] = Decimal('-100.00')
        samochod = Samochod(**self.samochod_data)

        with self.assertRaises(ValueError):
            samochod.save()
        print("TEST 5 PASS: ValueError wyrzucony dla ujemnej ceny")

    def test_06_walidacja_ujemnej_liczby_miejsc(self):
        """TEST 6: Ujemna liczba miejsc powinna wyrzucić ValueError"""
        self.samochod_data['liczba_miejsc'] = -5
        samochod = Samochod(**self.samochod_data)

        with self.assertRaises(ValueError):
            samochod.save()
        print("TEST 6 PASS: ValueError wyrzucony dla ujemnej liczby miejsc")

    def test_07_walidacja_ujemnej_predkosci(self):
        """TEST 7: Ujemna prędkość maksymalna powinna wyrzucić ValueError"""
        self.samochod_data['predkosc_maksymalna'] = -250
        samochod = Samochod(**self.samochod_data)

        with self.assertRaises(ValueError):
            samochod.save()
        print("TEST 7 PASS: ValueError wyrzucony dla ujemnej prędkości")

    def test_08_akceptacja_wartosci_zerowych(self):
        """TEST 8: Wartości zerowe powinny być zaakceptowane"""
        self.samochod_data['liczba_miejsc'] = 0
        self.samochod_data['moc'] = 0
        samochod = Samochod.objects.create(**self.samochod_data)

        self.assertEqual(samochod.liczba_miejsc, 0)
        self.assertEqual(samochod.moc, 0)
        print("TEST 8 PASS: Wartości zerowe zaakceptowane")

    def test_09_akceptacja_poprawnych_wartosci(self):
        """TEST 9: Prawidłowe wartości powinny być zaakceptowane"""
        samochod = Samochod.objects.filter(nazwa='BMW M5').first()

        self.assertIsNotNone(samochod.kod_samochodu)
        self.assertEqual(samochod.moc, 625)
        self.assertEqual(samochod.cena_za_dobe, Decimal('500.00'))
        self.assertEqual(samochod.liczba_miejsc, 5)
        print("TEST 9 PASS: Wszystkie wartości prawidłowe zaakceptowane")

    def test_10_edycja_zachowuje_kod(self):
        """TEST 10: Edycja samochodu nie powinna zmienić kodu"""
        oryginalny_kod = self.samochod.kod_samochodu
        self.samochod.moc = 750
        self.samochod.save()

        self.assertEqual(self.samochod.kod_samochodu, oryginalny_kod)
        print("TEST 10 PASS: Kod zachowany podczas edycji")

    def test_11_wszystkie_typy_skrzyn(self):
        """TEST 11: Wszystkie typy skrzyn biegów powinny być akceptowane"""
        skrzynie = ['manualna', 'automatyczna']

        for i, skrznia in enumerate(skrzynie):
            self.samochod_data['nazwa'] = f'Auto_{skrznia}'
            self.samochod_data['skrzynia_biegow'] = skrznia
            samochod = Samochod.objects.create(**self.samochod_data)
            self.assertEqual(samochod.skrzynia_biegow, skrznia)

        print("TEST 11 PASS: Wszystkie typy skrzyn (manualna, automatyczna) działają")

    def test_12_wszystkie_typy_napedow(self):
        """TEST 12: Wszystkie typy napędów powinny być akceptowane"""
        napedy = ['rwd', 'awd', 'fwd']

        for naped in napedy:
            self.samochod_data['nazwa'] = f'Auto_{naped}'
            self.samochod_data['naped'] = naped
            samochod = Samochod.objects.create(**self.samochod_data)
            self.assertEqual(samochod.naped, naped)

        print("TEST 12 PASS: Wszystkie napędy (RWD, AWD, FWD) działają")

    # ============ TESTY METODY MA_AKTYWNA_REZERWACJE() ============

    def test_13_brak_rezerwacji_zwraca_false(self):
        """TEST 13: Samochód bez rezerwacji powinien zwrócić False"""
        wynik = self.samochod.ma_aktywna_rezerwacje()
        self.assertFalse(wynik)
        print("TEST 13 PASS: Brak rezerwacji zwraca False")

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
