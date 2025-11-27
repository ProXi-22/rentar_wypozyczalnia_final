from django.shortcuts import render,redirect,get_object_or_404
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q,Sum,Count,F
from django.utils import timezone
from datetime import datetime,timedelta
from decimal import Decimal
from .models import Samochod,Rezerwacja,Uzytkownik
from .forms import (RegisterForm,LoginForm,DodajSamochodForm,EdytujSamochodForm,RezerwacjaForm,FiltrSamochodowForm,DodajPracownikaForm,EdytujPracownikaForm,RaportForm)

def sprawdz_role(user,wymagana_rola):
    try:uzytkownik=Uzytkownik.objects.get(user=user);return uzytkownik.rola==wymagana_rola
    except Uzytkownik.DoesNotExist:return False

def sprawdz_role_admin(user):
    try:uzytkownik=Uzytkownik.objects.get(user=user);return uzytkownik.rola=='admin'
    except Uzytkownik.DoesNotExist:return False

def sprawdz_role_pracownik_lub_admin(user):
    try:uzytkownik=Uzytkownik.objects.get(user=user);return uzytkownik.rola in['pracownik','admin']
    except Uzytkownik.DoesNotExist:return False

def index(request):
    samochody=Samochod.objects.filter(status='dostepny')[:6]
    liczba_samochodow=Samochod.objects.count()
    liczba_rezerwacji=Rezerwacja.objects.filter(status__in=['potwierdzony']).count()
    context={'samochody':samochody,'liczba_samochodow':liczba_samochodow,'liczba_rezerwacji':liczba_rezerwacji}
    return render(request,'index.html',context)

def register(request):
    if request.user.is_authenticated:return redirect('index')
    if request.method=='POST':
        form=RegisterForm(request.POST)
        if form.is_valid():
            user=form.save()
            Uzytkownik.objects.create(user=user,rola='klient')
            messages.success(request,'Konto zostało utworzone. Zaloguj się teraz.')
            return redirect('login')
        else:
            for field,errors in form.errors.items():
                for error in errors:messages.error(request,f"{field}: {error}")
    else:form=RegisterForm()
    return render(request,'register.html',{'form':form})

def login_view(request):
    if request.user.is_authenticated:return redirect('index')
    if request.method=='POST':
        form=LoginForm(request.POST)
        if form.is_valid():
            username=form.cleaned_data['username']
            password=form.cleaned_data['password']
            user=authenticate(request,username=username,password=password)
            if user is not None:
                login(request,user)
                messages.success(request,f'Witaj {user.username}!')
                return redirect('index')
            else:messages.error(request,'Błędna nazwa użytkownika lub hasło.')
    else:form=LoginForm()
    return render(request,'login.html',{'form':form})

@login_required(login_url='login')
def logout_view(request):
    logout(request)
    messages.success(request,'Wylogowano pomyślnie.')
    return redirect('index')

def cars_list(request):
    samochody=Samochod.objects.filter(status='dostepny')
    form=FiltrSamochodowForm(request.GET)
    if form.is_valid():
        if form.cleaned_data.get('nazwa'):samochody=samochody.filter(nazwa__icontains=form.cleaned_data['nazwa'])
        if form.cleaned_data.get('cena_od'):samochody=samochody.filter(cena_za_dobe__gte=form.cleaned_data['cena_od'])
        if form.cleaned_data.get('cena_do'):samochody=samochody.filter(cena_za_dobe__lte=form.cleaned_data['cena_do'])
        if form.cleaned_data.get('moc_od'):samochody=samochody.filter(moc__gte=form.cleaned_data['moc_od'])
        if form.cleaned_data.get('moc_do'):samochody=samochody.filter(moc__lte=form.cleaned_data['moc_do'])
        if form.cleaned_data.get('sortowanie'):samochody=samochody.order_by(form.cleaned_data['sortowanie'])
    context={'samochody':samochody,'form':form}
    return render(request,'cars.html',context)

@login_required(login_url='login')
def rezerwacja_samochodu(request, samochod_id):
    samochod = get_object_or_404(Samochod, id=samochod_id)

    try:
        uzytkownik = Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola != 'klient':
            messages.error(request, 'Tylko klienci mogą rezerwować samochody.')
            return redirect('cars_list')
    except Uzytkownik.DoesNotExist:
        messages.error(request, 'Błąd: profil użytkownika nie istnieje.')
        return redirect('cars_list')

    if request.method == 'POST':
        form = RezerwacjaForm(request.POST)
        if form.is_valid():
            rezerwacja = form.save(commit=False)
            rezerwacja.klient = request.user
            rezerwacja.samochod = samochod

            try:
                rezerwacja.save()
                messages.success(request, 'Rezerwacja złożona. Oczekuje na potwierdzenie pracownika.')
                return redirect('moje_rezerwacje')
            except ValueError as e:
                messages.error(request, str(e))
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, str(error))
    else:
        form = RezerwacjaForm()
        form._samochod = samochod

        rezerwacje_zajete = Rezerwacja.objects.filter(
            samochod=samochod,
            status__in=['oczekujacy', 'potwierdzony']
        ).order_by('data_odbioru')

        zajete_dni = []
        for rez in rezerwacje_zajete:
            zajete_dni.append(
                f"Od {rez.data_odbioru.strftime('%d/%m/%Y %H:%M')} do {rez.data_zwrotu.strftime('%d/%m/%Y %H:%M')}")

    context = {
        'form': form,
        'samochod': samochod,
        'zajete_dni': zajete_dni,
    }
    return render(request, 'rezerwacja.html', context)


@login_required(login_url='login')
def moje_rezerwacje(request):
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola!='klient':
            messages.error(request,'Dostęp tylko dla klientów.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    rezerwacje=Rezerwacja.objects.filter(klient=request.user).order_by('-data_utworzenia')
    context={'rezerwacje':rezerwacje}
    return render(request,'moje_rezerwacje.html',context)

@login_required(login_url='login')
def anuluj_rezerwacje(request,rezerwacja_id):
    rezerwacja=get_object_or_404(Rezerwacja,id=rezerwacja_id)
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola=='klient':
            if rezerwacja.klient!=request.user:
                messages.error(request,'Nie masz dostępu do tej rezerwacji.')
                return redirect('moje_rezerwacje')
            if rezerwacja.status not in['oczekujacy','potwierdzony']:
                messages.error(request,'Nie można anulować tej rezerwacji.')
                return redirect('moje_rezerwacje')
            rezerwacja.status='anulowany'
            rezerwacja.save()
            messages.success(request,'Rezerwacja anulowana.')
            return redirect('moje_rezerwacje')
        elif uzytkownik.rola in['pracownik','admin']:
            if rezerwacja.status not in['oczekujacy','potwierdzony']:
                messages.error(request,'Nie można anulować tej rezerwacji.')
                return redirect('panel_pracownika')
            rezerwacja.status='anulowany'
            rezerwacja.save()
            messages.success(request,'Rezerwacja anulowana.')
            return redirect('panel_pracownika')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')

@login_required(login_url='login')
def potwierdz_rezerwacje(request,rezerwacja_id):
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola not in['pracownik','admin']:
            messages.error(request,'Dostęp tylko dla pracowników.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    rezerwacja=get_object_or_404(Rezerwacja,id=rezerwacja_id)
    if rezerwacja.status=='oczekujacy':
        rezerwacja.status='potwierdzony'
        rezerwacja.pracownik_potwierdzajacy=request.user
        rezerwacja.save()
        messages.success(request,f'Rezerwacja {rezerwacja.kod_rezerwacji} potwierdzona.')
    else:messages.error(request,'Rezerwacja ma już inny status.')
    return redirect('panel_pracownika')

@login_required(login_url='login')
def panel_pracownika(request):
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola not in['pracownik','admin']:
            messages.error(request,'Dostęp tylko dla pracowników.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    rezerwacje=Rezerwacja.objects.order_by('-data_utworzenia')
    context={'rezerwacje':rezerwacje}
    return render(request,'panel_pracownika.html',context)

@login_required(login_url='login')
def zarzadzanie_samochodami(request):
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola not in['pracownik','admin']:
            messages.error(request,'Dostęp tylko dla pracowników.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    samochody=Samochod.objects.all()
    context={'samochody':samochody}
    return render(request,'zarzadzanie_samochodami.html',context)

@login_required(login_url='login')
def dodaj_samochod(request):
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola not in['pracownik','admin']:
            messages.error(request,'Dostęp tylko dla pracowników.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    if request.method=='POST':
        form=DodajSamochodForm(request.POST,request.FILES)
        if form.is_valid():
            try:
                samochod=form.save()
                messages.success(request,f'Samochód {samochod.nazwa} dodany pomyślnie.')
                return redirect('zarzadzanie_samochodami')
            except ValueError as e:messages.error(request,str(e))
        else:
            for field,errors in form.errors.items():
                for error in errors:messages.error(request,str(error))
    else:form=DodajSamochodForm()
    context={'form':form,'title':'Dodaj samochód'}
    return render(request,'edycja_samochodu.html',context)

@login_required(login_url='login')
def edytuj_samochod(request,samochod_id):
    samochod=get_object_or_404(Samochod,id=samochod_id)
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola not in['pracownik','admin']:
            messages.error(request,'Dostęp tylko dla pracowników.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    if request.method=='POST':
        form=EdytujSamochodForm(request.POST,request.FILES,instance=samochod)
        if form.is_valid():
            try:
                samochod=form.save()
                messages.success(request,f'Samochód {samochod.nazwa} zaktualizowany.')
                return redirect('zarzadzanie_samochodami')
            except ValueError as e:messages.error(request,str(e))
        else:
            for field,errors in form.errors.items():
                for error in errors:messages.error(request,str(error))
    else:form=EdytujSamochodForm(instance=samochod)
    context={'form':form,'samochod':samochod,'title':f'Edytuj {samochod.nazwa}'}
    return render(request,'edycja_samochodu.html',context)

@login_required(login_url='login')
def usun_samochod(request,samochod_id):
    samochod=get_object_or_404(Samochod,id=samochod_id)
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola not in['pracownik','admin']:
            messages.error(request,'Dostęp tylko dla pracowników.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    if samochod.ma_aktywna_rezerwacje():
        messages.error(request,'Nie można usunąć samochodu z aktywnymi rezerwacjami.')
        return redirect('zarzadzanie_samochodami')
    nazwa=samochod.nazwa
    samochod.delete()
    messages.success(request,f'Samochód {nazwa} usunięty.')
    return redirect('zarzadzanie_samochodami')

@login_required(login_url='login')
def zarzadzanie_uzytkownikami(request):
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola!='admin':
            messages.error(request,'Dostęp tylko dla administratorów.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    pracownicy=User.objects.filter(uzytkownik__rola__in=['pracownik','admin']).exclude(id=request.user.id)
    context={'pracownicy':pracownicy}
    return render(request,'zarzadzanie_uzytkownikami.html',context)

@login_required(login_url='login')
def dodaj_pracownika(request):
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola!='admin':
            messages.error(request,'Dostęp tylko dla administratorów.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    if request.method=='POST':
        form=DodajPracownikaForm(request.POST)
        if form.is_valid():
            user=User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data.get('first_name',''),
                last_name=form.cleaned_data.get('last_name',''),
                password=form.cleaned_data['password1']
            )
            rola=form.cleaned_data['rola']
            Uzytkownik.objects.create(user=user,rola=rola)
            messages.success(request,f'Pracownik {user.username} ({rola}) dodany.')
            return redirect('zarzadzanie_uzytkownikami')
        else:
            for field,errors in form.errors.items():
                for error in errors:messages.error(request,str(error))
    else:form=DodajPracownikaForm()
    context={'form':form,'title':'Dodaj pracownika'}
    return render(request,'edycja_uzytkownika.html',context)

@login_required(login_url='login')
def edytuj_pracownika(request,uzytkownik_id):
    uzytkownik_profil=get_object_or_404(Uzytkownik,id=uzytkownik_id)
    user=uzytkownik_profil.user
    try:
        current_uzytkownik=Uzytkownik.objects.get(user=request.user)
        if current_uzytkownik.rola!='admin':
            messages.error(request,'Dostęp tylko dla administratorów.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    if request.method=='POST':
        form=EdytujPracownikaForm(request.POST,instance=user)
        if form.is_valid():
            user=form.save()
            rola=request.POST.get('rola',uzytkownik_profil.rola)
            uzytkownik_profil.rola=rola
            uzytkownik_profil.save()
            messages.success(request,f'Pracownik {user.username} zaktualizowany.')
            return redirect('zarzadzanie_uzytkownikami')
    else:form=EdytujPracownikaForm(instance=user)
    context={'form':form,'uzytkownik_profil':uzytkownik_profil,'title':f'Edytuj {user.username}'}
    return render(request,'edycja_uzytkownika.html',context)

@login_required(login_url='login')
def usun_pracownika(request,uzytkownik_id):
    uzytkownik_profil=get_object_or_404(Uzytkownik,id=uzytkownik_id)
    try:
        current_uzytkownik=Uzytkownik.objects.get(user=request.user)
        if current_uzytkownik.rola!='admin':
            messages.error(request,'Dostęp tylko dla administratorów.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    username=uzytkownik_profil.user.username
    uzytkownik_profil.user.delete()
    messages.success(request,f'Pracownik {username} usunięty.')
    return redirect('zarzadzanie_uzytkownikami')

@login_required(login_url='login')
def raporty(request):
    try:
        uzytkownik=Uzytkownik.objects.get(user=request.user)
        if uzytkownik.rola!='admin':
            messages.error(request,'Dostęp tylko dla administratorów.')
            return redirect('index')
    except Uzytkownik.DoesNotExist:
        messages.error(request,'Błąd: profil użytkownika nie istnieje.')
        return redirect('index')
    form=RaportForm(request.GET)
    raport_data=None
    typ_raportu=None
    if form.is_valid():
        typ_raportu=form.cleaned_data.get('typ_raportu')
        okres=form.cleaned_data.get('okres')
        data_od=form.cleaned_data.get('data_od')
        data_do=form.cleaned_data.get('data_do')
        now=timezone.now().date()
        if okres=='dzien':
            data_od=now
            data_do=now+timedelta(days=1)
        elif okres=='tydzien':
            data_od=now-timedelta(days=now.weekday())
            data_do=data_od+timedelta(days=7)
        elif okres=='miesiac':
            data_od=now.replace(day=1)
            if now.month==12:data_do=now.replace(year=now.year+1,month=1,day=1)
            else:data_do=now.replace(month=now.month+1,day=1)
        elif okres=='rok':
            data_od=now.replace(month=1,day=1)
            data_do=now.replace(year=now.year+1,month=1,day=1)
        data_od_dt=timezone.make_aware(datetime.combine(data_od,datetime.min.time()))
        data_do_dt=timezone.make_aware(datetime.combine(data_do,datetime.min.time()))
        rezerwacje=Rezerwacja.objects.filter(data_utworzenia__gte=data_od_dt,data_utworzenia__lt=data_do_dt,status__in=['potwierdzony','zakonczony'])
        if typ_raportu=='zyski':
            zyski=rezerwacje.aggregate(total=Sum('kwota_razem'))['total']or Decimal('0')
            raport_data={'typ':'Zyski','wartosc':zyski,'okres':f"{data_od} do {data_do}",'liczba_rezerwacji':rezerwacje.count()}
        elif typ_raportu=='popularne':
            popularne=rezerwacje.values('samochod__nazwa').annotate(liczba=Count('id'),przychod=Sum('kwota_razem')).order_by('-liczba')[:10]
            raport_data={'typ':'Najpopularniejsze samochody','dane':list(popularne)}
        elif typ_raportu=='pracownicy':
            pracownicy=rezerwacje.values('pracownik_potwierdzajacy__username','pracownik_potwierdzajacy__first_name').annotate(liczba_rezerwacji=Count('id'),przychod=Sum('kwota_razem')).order_by('-liczba_rezerwacji')
            raport_data={'typ':'Raport pracowników','dane':list(pracownicy)}
    context={'form':form,'raport_data':raport_data}
    return render(request,'raporty.html',context)
