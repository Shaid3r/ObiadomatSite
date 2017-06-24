from django.contrib import admin
from .models import *


class DanieAdmin(admin.ModelAdmin):
    list_display = ['nazwa', 'cena']


class SesjaObiadowaAdmin(admin.ModelAdmin):
    list_display = ['tworca', 'jadlodajnia', 'data_obiadu', 'godzina_obiadu']


class ZamowienieInline(admin.TabularInline):
    model = Zamowienie


class ZamowieniaAdmin(admin.ModelAdmin):
    list_display = ['klient', 'data_obiadu', 'godzina_obiadu']

    def data_obiadu(self, obj):
        return obj.sesja_obiadowa.data_obiadu

    def godzina_obiadu(self, obj):
        return obj.sesja_obiadowa.godzina_obiadu

    inlines = [ZamowienieInline]


admin.site.register(Jadlodajnia)
admin.site.register(SesjaObiadowa, SesjaObiadowaAdmin)
admin.site.register(Danie, DanieAdmin)
admin.site.register(Zamowienia, ZamowieniaAdmin)