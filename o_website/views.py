# -*- coding: utf-8 -*-
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.core.mail import send_mass_mail, send_mail
from django.http import HttpResponseRedirect, Http404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from o_website.forms import *
from o_website.models import SesjaObiadowa, Zamowienia, Danie
import datetime


def home(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect(reverse('profile'))
    else:
        if request.method == 'POST':
            form = UserForm(request.POST)
            if form.is_valid():
                user = form.save()
                user.set_password(user.password)
                user.save()
                return HttpResponseRedirect("{}?new".format(reverse('home')))
        else:
            form = UserForm()
    return render(request, "o_website/home.html", {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST.get('username')

            if User.objects.filter(username=username):
                password = request.POST.get('password')
                user = authenticate(username=username, password=password)

                if user is not None:
                    login(request, user)
                    return HttpResponseRedirect(reverse('profile'))
                else:
                    form.add_error(None, "Błędne hasło. Spróbuj ponownie.")

            else:
                form.add_error(None, "Użytkownik nie istnieje.")

    else:
        form = LoginForm()

    return render(request, "o_website/login.html", {'form': form, 'no_navbarform': True})


@login_required(redirect_field_name=None)
def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


@login_required(redirect_field_name=None)
def profile(request):
    return render(request, "o_website/profile.html", {})


@login_required(redirect_field_name=None)
def edit_profile(request):
    if request.method == 'POST':
        form = EditProfileForm(request.POST, instance=request.user, user=request.user)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect("{}?success=edited_profile".format(reverse('profile')))
    else:
        form = EditProfileForm(instance=request.user, user=request.user)
    return render(request, "o_website/edit_profile.html", {'form': form})


@login_required(redirect_field_name=None)
def change_password(request):
    if request.method == 'POST':
        form = ChangePasswordForm(request.POST)
        if form.is_valid():
            password = request.POST.get('password')
            if request.user.check_password(password):
                password = request.POST.get('new_password')
                user = request.user
                user.set_password(password)
                user.save()
                update_session_auth_hash(request, user)
                return HttpResponseRedirect("{}?success=changed_password".format(reverse('profile')))
            else:
                form.add_error('password', "Błędne hasło. Spróbuj ponownie.")
    else:
        form = ChangePasswordForm()
    return render(request, "o_website/change_password.html", {'form': form})


@login_required(redirect_field_name=None)
def stworz_so(request):
    if request.method == 'POST':
        form = SesjaObiadowaForm(request.POST)
        if form.is_valid():
            import obiadomat.settings
            so = form.save(commit=False)
            so.tworca = request.user
            so.save()
            form.save_m2m()
            subject = "Obiadomat - Nowa sesja obiadowa!"
            message = "Możesz dołączyć do nowej sesji obiadowej i złożyć zamówienie pod adresem: {}".format(
                request.build_absolute_uri(reverse('zamow', args=(so.id,)))
            )
            datatuple = ()
            for email in so.all_emails():
                datatuple += ((subject, message, obiadomat.settings.EMAIL_HOST_USER, [email]),)
            #send_mass_mail(datatuple, fail_silently=False)
            return HttpResponseRedirect("{}?success=added_so".format(reverse('twoje_so')))
    else:
        form = SesjaObiadowaForm()

    return render(request, "o_website/stworz_so.html", {'form': form})


@login_required(redirect_field_name=None)
def edytuj_so(request, so_id):
    so = get_object_or_404(SesjaObiadowa, id=so_id)
    if so.data_obiadu > datetime.date.today()\
            or so.data_obiadu == datetime.date.today()\
            and so.godzina_obiadu > datetime.datetime.now().time():
        if so.tworca == request.user:
            zamowienia = so.zamowienia_set.all()
            if request.method == 'POST':
                form = SesjaObiadowaForm(request.POST, instance=so)
                if form.is_valid():
                    form.save()
                    return HttpResponseRedirect("{}?success=edited_so".format(reverse('twoje_so')))
            else:
                form = SesjaObiadowaForm(instance=so)
            return render(request, "o_website/edytuj_so.html", {'form': form, 'zamowienia': zamowienia})
    raise Http404


@login_required(redirect_field_name=None)
def twoje_so(request):
    so = SesjaObiadowa.objects.filter(
        Q(tworca=request.user) & (
            Q(data_obiadu__gt=datetime.date.today()) |
            Q(data_obiadu=datetime.date.today()) &
            Q(godzina_obiadu__gte=datetime.datetime.now().time())
        )
    ).order_by('data_obiadu', 'godzina_obiadu')
    return render(request, "o_website/twoje_so.html", {'so': so})


@login_required(redirect_field_name=None)
def raport(request, so_id):
    if SesjaObiadowa.objects.get(id=so_id).tworca != request.user:
        raise Http404
    so = SesjaObiadowa.objects.get(id=so_id).zamowienia_set.all()
    total_price = 0
    for e in so:
        total_price += e.total_price()
    return render(request, "o_website/raport.html", {'so': so, 'total_price': total_price})


@login_required(redirect_field_name=None)
def twoje_zamowienia(request):
    zamowienia = Zamowienia.objects.filter(
        Q(klient=request.user) & (
            Q(sesja_obiadowa__data_zamowien__gt=datetime.date.today()) |
            Q(sesja_obiadowa__data_zamowien=datetime.date.today()) &
            Q(sesja_obiadowa__godzina_zamowien__gte=datetime.datetime.now().time()) |
            Q(sesja_obiadowa__tworca=request.user) & (
                Q(sesja_obiadowa__data_obiadu__gt=datetime.date.today()) |
                Q(sesja_obiadowa__data_obiadu=datetime.date.today()) &
                Q(sesja_obiadowa__godzina_obiadu__gte=datetime.datetime.now().time())
            )
        )
    ).distinct()

    so = SesjaObiadowa.objects.filter(
        (
            Q(tworca=request.user) | (
                Q(doz_uzytkownicy=request.user) |
                Q(doz_grupy=request.user.groups.all())
            ) & (
                Q(data_zamowien__gt=datetime.date.today()) |
                Q(data_zamowien=datetime.date.today()) &
                Q(godzina_zamowien__gte=datetime.datetime.now().time())
            )
        ) & (
            Q(data_obiadu__gt=datetime.date.today()) |
            Q(data_obiadu=datetime.date.today()) &
            Q(godzina_obiadu__gte=datetime.datetime.now().time())
        )
    ).order_by('-data_obiadu', '-godzina_obiadu').distinct()

    for e in so:
        if e.zamowienia_set.filter(klient=request.user):
            so = so.exclude(pk=e.pk)

    context = {
        'zamowienia': zamowienia,
        'so': so,
    }
    return render(request, "o_website/twoje_zamowienia.html", context)


@login_required(redirect_field_name=None)
def zamow(request, so_id):
    so = SesjaObiadowa.objects.get(id=so_id)
    if Zamowienia.objects.filter(klient=request.user, sesja_obiadowa__id=so_id):
        raise Http404
    elif so.data_obiadu < datetime.date.today()\
            or so.data_obiadu == datetime.date.today()\
            and so.godzina_obiadu < datetime.datetime.now().time():
        return HttpResponseRedirect("{}?error=expired_dinner".format(reverse('twoje_zamowienia')))
    else:
        bad_date = so.data_zamowien < datetime.date.today()\
            or so.data_zamowien == datetime.date.today()\
            and so.godzina_zamowien < datetime.datetime.now().time()

        if bad_date and so.tworca != request.user:
            return HttpResponseRedirect("{}?error=expired_order".format(reverse('twoje_zamowienia')))
        else:
            if request.method == 'POST':
                form = ZamowieniaForm(request.POST)
                zform = ZamowienieForm(request.POST)

                if form.is_valid() and zform.is_valid():
                    empty = True
                    zamowienia = form.save(commit=False)
                    zamowienia.klient = request.user
                    zamowienia.sesja_obiadowa = SesjaObiadowa.objects.get(id=so_id)
                    zamowienia.save()
                    ilosc = request.POST.getlist('ilosc')
                    for x, y in zip(Danie.objects.all(), ilosc):
                        if int(y) > 0:
                            empty = False
                            zam = Zamowienie(zamowienia=zamowienia, danie=x, ilosc=y)
                            zam.save()
                    if not empty:
                        return HttpResponseRedirect("{}?success=added_order".format(reverse('twoje_zamowienia')))
                    zamowienia.delete()
                    form.add_error(None, "Nie wybrałes żadnego dania.")
            else:
                form = ZamowieniaForm()
                zform = ZamowienieForm()

    context = {
        'form': form,
        'zform': zform,
        'warning': bad_date,
        'dania': Danie.objects.all()
    }

    return render(request, "o_website/zamow.html", context)


@login_required(redirect_field_name=None)
def zamowienie(request, z_id):
    order = Zamowienia.objects.get(id=z_id)
    if order.klient != request.user and order.sesja_obiadowa.tworca != request.user:
        raise Http404
    else:
        zam = order.zamowienie_set.all()
    return render(request, "o_website/zamowienie.html", {'zamowienie': order, 'zam': zam})


@login_required(redirect_field_name=None)
def edytuj_zamowienie(request, z_id):
    order = Zamowienia.objects.get(id=z_id)
    error = False
    if order.klient != request.user and order.sesja_obiadowa.tworca != request.user:
        raise Http404
    elif order.sesja_obiadowa.data_obiadu < datetime.date.today()\
            or order.sesja_obiadowa.data_obiadu == datetime.date.today()\
            and order.sesja_obiadowa.godzina_obiadu < datetime.datetime.now().time():
        return HttpResponseRedirect("{}?error=expired_dinner".format(reverse('twoje_zamowienia')))
    else:
        bad_date = order.sesja_obiadowa.data_zamowien < datetime.date.today()\
            or order.sesja_obiadowa.data_zamowien == datetime.date.today()\
            and order.sesja_obiadowa.godzina_zamowien < datetime.datetime.now().time()

        if bad_date and order.sesja_obiadowa.tworca != request.user:
            return HttpResponseRedirect("{}?error=expired_order".format(reverse('twoje_zamowienia')))
        else:
            if request.method == 'POST':
                form = ZamowieniaForm(request.POST, instance=order)
                ilosc_list = request.POST.getlist('ilosc')
                try:
                    ilosc_list = [int(e) for e in ilosc_list]
                except ValueError:
                    error = True
                if not error and form.is_valid():
                    form.save()
                    for x, y in zip(Danie.objects.all(), ilosc_list):
                        if y == 0 and x.zamowienie_set.filter(zamowienia__id=z_id):
                            x.zamowienie_set.get(zamowienia__id=z_id).delete()
                        elif y > 0 and x.zamowienie_set.filter(zamowienia__id=z_id):
                            obj = Zamowienie.objects.get(zamowienia__id=z_id, danie=x)
                            obj.ilosc = y
                            obj.save()
                        elif y > 0:
                            zam = Zamowienie(zamowienia=order, danie=x, ilosc=y)
                            zam.save()
                    if order.sesja_obiadowa.tworca == request.user and order.klient != request.user:
                        import obiadomat.settings
                        subject = "Obiadomat - Twoje zamówienie zostało zmienione"
                        message = "Twórca sesji zmienił twoje zamówienie. Szczegóły pod adresem: {}".format(
                            request.build_absolute_uri(reverse('zamowienie', args=(z_id,)))
                        )
                        recipient_list = [order.klient.email]
                        send_mail(
                            subject, message, obiadomat.settings.EMAIL_HOST_USER, recipient_list, fail_silently=True
                        )
                    return HttpResponseRedirect("{}?success=edited_order".format(reverse('zamowienie', args=(z_id,))))
            else:
                form = ZamowieniaForm(instance=order)

        dania = []

        for e in Danie.objects.all():
            dania.append(e.zam(z_id=z_id))

        context = {
            'form': form,
            'warning': bad_date,
            'error': error,
            'dania': dania
        }
    return render(request, "o_website/edytuj_zamowienie.html", context)


@login_required(redirect_field_name=None)
def usun_zamowienie(request, z_id):
    order = Zamowienia.objects.get(id=z_id)
    if order.klient != request.user and order.sesja_obiadowa.tworca != request.user:
        raise Http404
    elif order.sesja_obiadowa.data_obiadu < datetime.date.today()\
            or order.sesja_obiadowa.data_obiadu == datetime.date.today()\
            and order.sesja_obiadowa.godzina_obiadu < datetime.datetime.now().time():
        return HttpResponseRedirect("{}?error=expired_dinner".format(reverse('twoje_zamowienia')))
    else:
        bad_date = order.sesja_obiadowa.data_zamowien < datetime.date.today()\
            or order.sesja_obiadowa.data_zamowien == datetime.date.today()\
            and order.sesja_obiadowa.godzina_zamowien < datetime.datetime.now().time()

        if bad_date and order.sesja_obiadowa.tworca != request.user:
            return HttpResponseRedirect("{}?error=expired_order".format(reverse('twoje_zamowienia')))
        else:
            order.delete()
    return HttpResponseRedirect("{}?success=deleted_order".format(reverse('twoje_zamowienia')))


@login_required(redirect_field_name=None)
def historia(request):
    so = request.user.zamowienia_set.filter(
        Q(sesja_obiadowa__data_obiadu__lt=datetime.date.today()) |
        Q(sesja_obiadowa__data_obiadu=datetime.date.today()) &
        Q(sesja_obiadowa__godzina_obiadu__lt=datetime.datetime.now().time())
    ).order_by('-sesja_obiadowa__data_obiadu', '-sesja_obiadowa__godzina_obiadu')

    so2 = SesjaObiadowa.objects.filter(
        Q(tworca=request.user) & (
            Q(data_obiadu__lt=datetime.date.today()) |
            Q(data_obiadu=datetime.date.today()) &
            Q(godzina_obiadu__lt=datetime.datetime.now().time())
        )
    ).order_by('-data_obiadu', '-godzina_obiadu')

    total_price = 0

    for e in so:
        total_price += e.total_price()

    context = {
        'so': so,
        'so2': so2,
        'total_price': total_price
    }
    return render(request, "o_website/historia.html", context)
