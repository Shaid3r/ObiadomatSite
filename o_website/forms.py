# -*- coding: utf-8 -*-
from django import forms
from django.contrib.auth.models import User
from o_website.models import SesjaObiadowa, Zamowienia, Zamowienie
import datetime


class UserForm(forms.ModelForm):
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="* Hasło (ponownie)")

    def __init__(self, *args, **kwargs):
        super(UserForm, self).__init__(*args, **kwargs)
        self.fields['email'].required = True

    def clean_email(self):
        data = self.cleaned_data['email']
        if User.objects.filter(email=data):
            raise forms.ValidationError("Podany email jest już używany.")

        return data

    def clean(self):
        cleaned_data = super(UserForm, self).clean()
        password = self.cleaned_data.get('password')
        password2 = self.cleaned_data.get('password2')

        if password != password2:
            self.add_error('password', "To pole jest wymagane.")
            self.add_error('password2', "Hasła różnią się.")

        return cleaned_data

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'password': forms.PasswordInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'username': "* Nazwa użytkownika",
            'email': "* Adres email",
            'password': "* Hasło"
        }


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nazwa użytkownika'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Hasło'}))


class EditProfileForm(forms.ModelForm):
    password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="* Hasło")

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        super(EditProfileForm, self).__init__(*args, **kwargs)

    def clean_password1(self):
        data = self.cleaned_data['password1']
        if not self.user.check_password(data):
            raise forms.ValidationError("Błędne hasło. Spróbuj ponownie.")
        return data

    def clean_email(self):
        data = self.cleaned_data['email']
        if self.user.email != data and User.objects.filter(email=data):
            raise forms.ValidationError("Podany email jest już używany.")

        return data

    class Meta:
        model = User
        fields = ['password1', 'first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }


class ChangePasswordForm(forms.Form):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Obecne hasło"
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nowe hasło"
    )
    new_password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Nowe hasło (ponownie)"
    )

    def clean(self):
        cleaned_data = super(ChangePasswordForm, self).clean()
        password = self.cleaned_data.get('new_password')
        password2 = self.cleaned_data.get('new_password2')

        if password != password2:
            self.add_error('new_password', "To pole jest wymagane.")
            self.add_error('new_password2', "Hasła różnią się.")

        return cleaned_data


class SesjaObiadowaForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(SesjaObiadowaForm, self).__init__(*args, **kwargs)
        self.fields['jadlodajnia'].empty_label = None

    def clean(self):
        cleaned_data = super(SesjaObiadowaForm, self).clean()
        data_obiadu = self.cleaned_data.get('data_obiadu')
        godzina_obiadu = self.cleaned_data.get('godzina_obiadu')
        data_zamowien = self.cleaned_data.get('data_zamowien')
        godzina_zamowien = self.cleaned_data.get('godzina_zamowien')

        if data_obiadu < datetime.date.today():
            self.add_error('data_obiadu', "Nie można podawać przeszłej daty.")
        elif data_obiadu == datetime.date.today() and godzina_obiadu < datetime.datetime.now().time():
            self.add_error('godzina_obiadu', "Nie można podawać przeszłej godziny.")

        if data_zamowien < datetime.date.today():
            self.add_error('data_zamowien', "Nie można podawać przeszłej daty.")
        elif data_zamowien == datetime.date.today() and godzina_zamowien < datetime.datetime.now().time():
            self.add_error('godzina_zamowien', "Nie można podawać przeszłej godziny.")

        if data_zamowien > data_obiadu:
            self.add_error('data_zamowien', "Data końca składania zamówień nie może być późniejsza niż data obiadu.")
        elif data_zamowien == data_obiadu and godzina_obiadu < godzina_zamowien:
            self.add_error('godzina_zamowien',
                           "Godzina końca składania zamówień nie może być późniejsza niż godzina obiadu.")

        return cleaned_data

    class Meta:
        model = SesjaObiadowa
        fields = ['jadlodajnia', 'data_obiadu', 'godzina_obiadu', 'data_zamowien', 'godzina_zamowien',
                  'doz_uzytkownicy', 'doz_grupy']
        widgets = {
            'jadlodajnia': forms.Select(attrs={'class': 'form-control'}),
            'data_obiadu': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'godzina_obiadu': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'data_zamowien': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}, format='%Y-%m-%d'),
            'godzina_zamowien': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'doz_uzytkownicy': forms.SelectMultiple(attrs={'class': 'selectpicker'}),
            'doz_grupy': forms.SelectMultiple(attrs={'class': 'selectpicker'}),
        }
        error_messages = {
            'data_obiadu': {
                'invalid': "Wpisz poprawną datę w formacie: rrrr-mm-dd",
            },
            'godzina_obiadu': {
                'invalid': "Wpisz poprawną godzinę w formacie: gg:mm:ss",
            },
            'data_zamowien': {
                'invalid': "Wpisz poprawną datę w formacie: rrrr-mm-dd",
            },
            'godzina_zamowien': {
                'invalid': "Wpisz poprawną godzinę w formacie: gg:mm:ss",
            },
        }


class ZamowieniaForm(forms.ModelForm):
    class Meta:
        model = Zamowienia
        fields = ['platnosc', 'uwagi']
        widgets = {
            'platnosc': forms.Select(attrs={'class': 'form-control'}),
            'uwagi': forms.Textarea(attrs={'class': 'form-control'}),
        }


class ZamowienieForm(forms.Form):
    ilosc = forms.IntegerField(initial='0', widget=forms.NumberInput(attrs={'class': 'form-control'}))
