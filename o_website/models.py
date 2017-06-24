# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User, Group
import datetime


class Jadlodajnia(models.Model):
    nazwa = models.CharField(max_length=50)

    def __str__(self):
        return self.nazwa

    class Meta:
        verbose_name = "Jadłodajnia"
        verbose_name_plural = "Jadłodajnie"


class SesjaObiadowa(models.Model):
    tworca = models.ForeignKey(User, verbose_name="twórca")
    doz_uzytkownicy = models.ManyToManyField(
        User,
        blank=True,
        related_name="doz_uzytkownicy",
        verbose_name="użytkownicy którzy mogą wziąść udział"
    )
    doz_grupy = models.ManyToManyField(Group, blank=True, verbose_name="grupy które mogą wziąść udział")
    jadlodajnia = models.ForeignKey(Jadlodajnia, verbose_name="jadłodajnia")
    data_obiadu = models.DateField(default="{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(days=2)))
    godzina_obiadu = models.TimeField(default="{:%H:%M}".format(datetime.datetime.now()))
    data_zamowien = models.DateField(
        default="{:%Y-%m-%d}".format(datetime.datetime.now() + datetime.timedelta(days=1)),
        verbose_name="data zamówień",
        help_text="Data do której można składać i edytować zamówienia"
    )
    godzina_zamowien = models.TimeField(
        default="{:%H:%M}".format(datetime.datetime.now()),
        verbose_name="godzina zamówień",
        help_text="Godzina do której można zamawiać i edytować zamówienia"
    )

    def __str__(self):
        return '%s, %s' % (self.tworca, self.jadlodajnia)

    def all_emails(self):
        emails = []
        for e in self.doz_uzytkownicy.all():
            emails.append(e.email)
        for e in self.doz_grupy.all():
            users = e.user_set.all()
            for user in users:
                if user.email not in emails:
                    emails.append(user.email)
        return emails

    class Meta:
        verbose_name_plural = "Sesje obiadowe"


class Danie(models.Model):
    nazwa = models.CharField(max_length=100)
    cena = models.DecimalField(max_digits=6, decimal_places=2)
    jadlodania = models.ForeignKey(Jadlodajnia)

    def __str__(self):
        return self.nazwa

    def zam(self, z_id):
        ilosc = 0
        if self.zamowienie_set.filter(zamowienia__id=z_id):
            ilosc = self.zamowienie_set.get(zamowienia__id=z_id).ilosc
        return self.nazwa, self.cena, ilosc

    class Meta:
        verbose_name_plural = "Dania"


class Zamowienia(models.Model):
    PLATNOSC_CHOICES = (
        (1, "gotówka"),
        (2, "karta"),
        (3, "kredyt"),
    )
    klient = models.ForeignKey(User)
    sesja_obiadowa = models.ForeignKey(SesjaObiadowa)
    platnosc = models.IntegerField(choices=PLATNOSC_CHOICES, default=1, verbose_name="płatność")
    uwagi = models.TextField(blank=True)

    def __str__(self):
        return self.klient.__str__()

    def total_price(self):
        t = 0
        for e in self.zamowienie_set.all():
            t += e.total_price()
        return t

    class Meta:
        verbose_name = "Zamówienia"
        verbose_name_plural = "Zamówienia"


class Zamowienie(models.Model):
    zamowienia = models.ForeignKey(Zamowienia)
    danie = models.ForeignKey(Danie)
    ilosc = models.PositiveIntegerField(default=0)

    def __str__(self):
        return "{}, {}".format(self.danie.nazwa, self.danie.cena)

    def total_price(self):
        return self.danie.cena * self.ilosc

    class Meta:
        verbose_name = "Zamówienie"
        verbose_name_plural = "Zamówienie"
