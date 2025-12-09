from django.test import TestCase
from django.contrib.auth.models import User
from rentar_app.models import Uzytkownik

class TestUzytkownikModel(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username='tempuser',
            password='tempuser123',
            email='tempuser@example.com'
        )
        self.uzytkownik = Uzytkownik.objects.create(
            user=self.user,
            rola='klient'
        )

    def test_01_uzytkownik_creation(self):
        self.assertEqual(self.uzytkownik.rola, 'klient')
        self.assertEqual(self.uzytkownik.user.username, 'tempuser')
        self.assertIsNotNone(self.uzytkownik.kod_uzytkownika)
        print("TEST 1 PASS: Uzytkownik utworzony z przypisanym kodem")

    def test_02_uzytkownik_auto_kod(self):
        self.assertEqual(self.uzytkownik.kod_uzytkownika, 'U00001')
        user2 = User.objects.create_user(username='user2', password='pass')
        uzytkownik2 = Uzytkownik.objects.create(user=user2, rola='pracownik')
        self.assertEqual(uzytkownik2.kod_uzytkownika, 'U00002')
        print("TEST 2 PASS: Kody auto-generowane: U00001, U00002")

    def test_03_uzytkownik_role_choices(self):
        roles = ['klient', 'pracownik', 'admin']
        for role in roles:
            user = User.objects.create_user(username=f'user_{role}', password='pass')
            uz = Uzytkownik.objects.create(user=user, rola=role)
            self.assertEqual(uz.rola, role)
        print("TEST 3 PASS: Wszystkie role działają: klient, pracownik, admin")

