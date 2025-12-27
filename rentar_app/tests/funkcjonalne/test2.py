from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from rentar_app.models import Uzytkownik, Samochod
from datetime import timedelta
from django.utils import timezone
import time

class FunctionalTestRezerwacjaSelenium(StaticLiveServerTestCase): #TESTY FUNKCJONALNE: Rezerwacja oraz UI

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.add_argument('--start-maximized')
        options.add_argument('--start-maximized')
        cls.selenium = webdriver.Chrome(options=options)
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        # Dane testowe
        self.klient = User.objects.create_user(
            username='klient_selenium',
            password='SelPass123!',
            email='sel@example.com'
        )
        Uzytkownik.objects.create(user=self.klient, rola='klient')
        self.samochod = Samochod.objects.create(
            nazwa='BMW 320i',
            rocznik=2023,
            pojemnosc_silnika='2.0',
            moc=184,
            przyspieszenie='7.8',
            predkosc_maksymalna=210,
            skrzynia_biegow='automatyczna',
            liczba_miejsc=5,
            naped='awd',
            cena_za_dobe=250.00,
            status='dostepny'
        )

    def test_functional_rezerwacja_full_flow(self):
        """FUNKCJONALNY: Pełny flow rezerwacji w przeglądarce"""
        
        # KROK 1: Otwórz stronę główną
        self.selenium.get(f'{self.live_server_url}/')
        time.sleep(1)
        print("KROK 1: Otwarta strona główna")
        
        # KROK 2: Kliknij logowanie
        login_link = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Zaloguj się'))
        )
        login_link.click()
        time.sleep(1)
        print("KROK 2: Otwarta strona logowania")
        
        # KROK 3: Zaloguj się
        username = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        password = self.selenium.find_element(By.NAME, 'password')
        username.send_keys('klient_selenium')
        password.send_keys('SelPass123!')
        submit_btn = self.selenium.find_element(By.XPATH, '//button[@type="submit"]')
        submit_btn.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Wyloguj'))
        )
        print("KROK 3: Zalogowany")
        time.sleep(1)
        
        # KROK 4: Przejdź do samochodów
        cars_link = self.selenium.find_element(By.LINK_TEXT, 'Samochody')
        cars_link.click()
        time.sleep(1)
        print("KROK 4: Otwarta lista samochodów")
        
        # KROK 5: Zarezerwuj samochód
        bmw_element = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "BMW")]'))
        )
        print("KROK 5a: Znaleziono BMW 320i")
        reserve_btn = WebDriverWait(self.selenium, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//button[contains(text(), "Rezerwuj")]'))
        )
        reserve_btn.click()
        print("KROK 5b: Otwarta forma rezerwacji")
        time.sleep(1)
        
        # KROK 6: Wypełnij formę
        date_from = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'data_odbioru'))
        )
        date_to = self.selenium.find_element(By.NAME, 'data_zwrotu')
        date_from.send_keys('01012026')
        date_to.send_keys('05012026')
        submit = self.selenium.find_element(By.XPATH, '//button[@type="submit"]')
        submit.click()
        print("KROK 6: Formularz wysłany")
        time.sleep(2)
        
        # KROK 7: Weryfikacja
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "BMW")]'))
        )
        print("KROK 7: Rezerwacja zapisana - widoczna na liście")

class FunctionalTestLoginSelenium(StaticLiveServerTestCase):
    """TESTY FUNKCJONALNE: Logowanie"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.selenium = webdriver.Chrome()
        cls.selenium.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )
        Uzytkownik.objects.create(user=self.user, rola='klient')

    def test_functional_login_success(self):
        """FUNKCJONALNY: Logowanie - poprawne dane"""
        self.selenium.get(f'{self.live_server_url}/login/')
        username = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        password = self.selenium.find_element(By.NAME, 'password')
        submit = self.selenium.find_element(By.XPATH, '//button[@type="submit"]')
        username.send_keys('testuser')
        password.send_keys('TestPass123!')
        submit.click()
        WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.LINK_TEXT, 'Wyloguj'))
        )
        print("LOGIN: Zalogowanie pomyślne")

    def test_functional_login_failure(self):
        """FUNKCJONALNY: Logowanie - błędne hasło"""
        self.selenium.get(f'{self.live_server_url}/login/')
        username = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        password = self.selenium.find_element(By.NAME, 'password')
        submit = self.selenium.find_element(By.XPATH, '//button[@type="submit"]')
        username.send_keys('testuser')
        password.send_keys('WRONGPASS')
        submit.click()
        time.sleep(2)
        error_msg = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.XPATH, '//*[contains(text(), "Błęd")]'))
        )
        self.assertIsNotNone(error_msg)
        print("LOGIN: Wyświetlony błąd dla złych danych")

# RUN ALL TESTS
if __name__ == '__main__':
    import unittest
    unittest.main(verbosity=2)