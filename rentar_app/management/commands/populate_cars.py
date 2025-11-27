from django.core.management.base import BaseCommand
from rentar_app.models import Samochod

class Command(BaseCommand):
    help = 'Populate database with 10 sports cars'
    
    def handle(self, *args, **options):
        if Samochod.objects.exists():
            self.stdout.write(self.style.WARNING('Baza danych już zawiera samochody. Pomijanie...'))
            return
        
        samochody = [
            {
                'nazwa': 'Ferrari F8 Tributo',
                'rocznik': 2023,
                'pojemnosc_silnika': '3.9L',
                'moc': 710,
                'przyspieszenie': '2.9s',
                'predkosc_maksymalna': 340,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 2,
                'naped': 'rwd',
                'cena_za_dobe': 2500.00,
                'status': 'dostepny',
            },
            {
                'nazwa': 'Lamborghini Huracan',
                'rocznik': 2023,
                'pojemnosc_silnika': '5.2L',
                'moc': 640,
                'przyspieszenie': '2.9s',
                'predkosc_maksymalna': 325,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 2,
                'naped': 'awd',
                'cena_za_dobe': 2200.00,
                'status': 'dostepny',
            },
            {
                'nazwa': 'Porsche 911 Carrera',
                'rocznik': 2023,
                'pojemnosc_silnika': '3.0L',
                'moc': 379,
                'przyspieszenie': '3.7s',
                'predkosc_maksymalna': 308,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 2,
                'naped': 'rwd',
                'cena_za_dobe': 1800.00,
                'status': 'dostepny',
            },
            {
                'nazwa': 'BMW M440i',
                'rocznik': 2023,
                'pojemnosc_silnika': '3.0L',
                'moc': 382,
                'przyspieszenie': '3.9s',
                'predkosc_maksymalna': 250,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 4,
                'naped': 'awd',
                'cena_za_dobe': 900.00,
                'status': 'dostepny',
            },
            {
                'nazwa': 'Mercedes AMG C63',
                'rocznik': 2022,
                'pojemnosc_silnika': '4.0L',
                'moc': 510,
                'przyspieszenie': '3.5s',
                'predkosc_maksymalna': 290,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 5,
                'naped': 'rwd',
                'cena_za_dobe': 1200.00,
                'status': 'dostepny',
            },
            {
                'nazwa': 'Audi RS6 Avant',
                'rocznik': 2023,
                'pojemnosc_silnika': '4.0L',
                'moc': 592,
                'przyspieszenie': '3.6s',
                'predkosc_maksymalna': 305,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 5,
                'naped': 'awd',
                'cena_za_dobe': 1500.00,
                'status': 'dostepny',
            },
            {
                'nazwa': 'McLaren 720S',
                'rocznik': 2023,
                'pojemnosc_silnika': '4.0L',
                'moc': 710,
                'przyspieszenie': '2.8s',
                'predkosc_maksymalna': 341,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 2,
                'naped': 'rwd',
                'cena_za_dobe': 2400.00,
                'status': 'dostepny',
            },
            {
                'nazwa': 'Corvette C8 Stingray',
                'rocznik': 2023,
                'pojemnosc_silnika': '5.5L',
                'moc': 495,
                'przyspieszenie': '2.9s',
                'predkosc_maksymalna': 299,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 2,
                'naped': 'rwd',
                'cena_za_dobe': 1400.00,
                'status': 'dostepny',
            },
            {
                'nazwa': 'Dodge Charger R/T',
                'rocznik': 2023,
                'pojemnosc_silnika': '5.7L',
                'moc': 370,
                'przyspieszenie': '4.2s',
                'predkosc_maksymalna': 290,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 5,
                'naped': 'rwd',
                'cena_za_dobe': 850.00,
                'status': 'dostepny',
            },
            {
                'nazwa': 'Nissan GT-R',
                'rocznik': 2023,
                'pojemnosc_silnika': '3.8L',
                'moc': 565,
                'przyspieszenie': '2.7s',
                'predkosc_maksymalna': 320,
                'skrzynia_biegow': 'automatyczna',
                'liczba_miejsc': 4,
                'naped': 'awd',
                'cena_za_dobe': 1300.00,
                'status': 'dostepny',
            },
        ]
        
        for samochod_data in samochody:
            samochod = Samochod.objects.create(**samochod_data)
            self.stdout.write(self.style.SUCCESS(f'✓ Dodano: {samochod.nazwa}'))
        
        self.stdout.write(self.style.SUCCESS('Pomyślnie dodano 10 samochodów!'))
