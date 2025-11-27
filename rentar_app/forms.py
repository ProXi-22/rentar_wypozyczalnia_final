from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Samochod, Rezerwacja, Uzytkownik
from django.utils import timezone


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=100, required=False)
    last_name = forms.CharField(max_length=100, required=False)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def clean(self):
        cleaned_data = super().clean()
        if len(cleaned_data.get('password1', '')) < 6:
            raise forms.ValidationError("Hasło musi mieć co najmniej 6 znaków")
        return cleaned_data


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class DodajSamochodForm(forms.ModelForm):
    class Meta:
        model = Samochod
        fields = ['nazwa', 'rocznik', 'pojemnosc_silnika', 'moc', 'przyspieszenie', 'predkosc_maksymalna', 'skrzynia_biegow', 'liczba_miejsc', 'naped', 'cena_za_dobe', 'status', 'zdjecie']
        widgets = {
            'nazwa': forms.TextInput(attrs={'class': 'form-control'}),
            'rocznik': forms.NumberInput(attrs={'class': 'form-control'}),
            'pojemnosc_silnika': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. 3.0'}),
            'moc': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'przyspieszenie': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. 3.5'}),
            'predkosc_maksymalna': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'skrzynia_biegow': forms.Select(attrs={'class': 'form-control'}),
            'liczba_miejsc': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'naped': forms.Select(attrs={'class': 'form-control'}),
            'cena_za_dobe': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-control'}),
            'zdjecie': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('moc', 0) < 0:
            raise forms.ValidationError("Moc nie może być ujemna")
        if cleaned_data.get('cena_za_dobe', 0) < 0:
            raise forms.ValidationError("Cena nie może być ujemna")
        if cleaned_data.get('liczba_miejsc', 0) < 0:
            raise forms.ValidationError("Liczba miejsc nie może być ujemna")
        if cleaned_data.get('predkosc_maksymalna', 0) < 0:
            raise forms.ValidationError("Prędkość maksymalna nie może być ujemna")
        if cleaned_data.get('rocznik', 0) < 1900:
            raise forms.ValidationError("Rocznik musi być prawidłowy")
        return cleaned_data


class EdytujSamochodForm(DodajSamochodForm):
    pass


class RezerwacjaForm(forms.ModelForm):
    class Meta:
        model = Rezerwacja
        fields = ['data_odbioru', 'data_zwrotu', 'miejsce_odbioru', 'miejsce_zwrotu']
        widgets = {
            'data_odbioru': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'min': timezone.now().isoformat()}),
            'data_zwrotu': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local', 'min': timezone.now().isoformat()}),
            'miejsce_odbioru': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Warszawa, ul. Marszałkowska 1'}),
            'miejsce_zwrotu': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'np. Kraków, Centrum'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        data_odbioru = cleaned_data.get('data_odbioru')
        data_zwrotu = cleaned_data.get('data_zwrotu')

        if data_odbioru and data_zwrotu:
            if data_zwrotu <= data_odbioru:
                raise forms.ValidationError("Data zwrotu musi być po dacie odbioru")
            if data_odbioru < timezone.now():
                raise forms.ValidationError("Data odbioru nie może być z przeszłości")
        return cleaned_data


class FiltrSamochodowForm(forms.Form):
    SORTOWANIE_CHOICES = [
        ('nazwa', 'Nazwa (A-Z)'),
        ('-nazwa', 'Nazwa (Z-A)'),
        ('cena_za_dobe', 'Cena (rosnąco)'),
        ('-cena_za_dobe', 'Cena (malejąco)'),
        ('moc', 'Moc (rosnąco)'),
        ('-moc', 'Moc (malejąco)'),
    ]

    cena_od = forms.DecimalField(required=False, min_value=0, label="Cena od")
    cena_do = forms.DecimalField(required=False, min_value=0, label="Cena do")
    moc_od = forms.IntegerField(required=False, min_value=0, label="Moc od")
    moc_do = forms.IntegerField(required=False, min_value=0, label="Moc do")
    nazwa = forms.CharField(max_length=100, required=False, label="Nazwa")
    sortowanie = forms.ChoiceField(choices=SORTOWANIE_CHOICES, required=False, label="Sortuj")


class DodajPracownikaForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput, label="Hasło")
    password2 = forms.CharField(widget=forms.PasswordInput, label="Powtórz hasło")
    rola = forms.ChoiceField(choices=[('pracownik', 'Pracownik'), ('admin', 'Administrator')])

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError("Hasła się nie zgadzają")
            if len(password1) < 6:
                raise forms.ValidationError("Hasło musi mieć co najmniej 6 znaków")
        return cleaned_data


class EdytujPracownikaForm(forms.ModelForm):
    rola = forms.ChoiceField(choices=[('pracownik', 'Pracownik'), ('admin', 'Administrator')])

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name')


class RaportForm(forms.Form):
    RAPORT_CHOICES = [
        ('zyski', 'Zyski'),
        ('popularne', 'Najpopularniejsze samochody'),
        ('pracownicy', 'Raport pracowników'),
    ]

    OKRES_CHOICES = [
        ('dzien', 'Dzień'),
        ('tydzien', 'Tydzień'),
        ('miesiac', 'Miesiąc'),
        ('rok', 'Rok'),
        ('custom', 'Niestandardowy okres'),
    ]

    typ_raportu = forms.ChoiceField(choices=RAPORT_CHOICES)
    okres = forms.ChoiceField(choices=OKRES_CHOICES)
    data_od = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    data_do = forms.DateField(required=False, widget=forms.DateInput(attrs={'type': 'date'}))
