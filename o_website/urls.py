from django.conf.urls import url
from o_website import views

urlpatterns = [
    url(r'^$', views.home, name='home'),
    url(r'^login$', views.login_view, name='login'),
    url(r'^logout$', views.logout_view, name='logout'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^edit-profile$', views.edit_profile, name='edit_profile'),
    url(r'^change-password$', views.change_password, name='change_password'),
    url(r'^stworz-sesje-obiadowa$', views.stworz_so, name='stworz_so'),
    url(r'^twoje-sesje-obiadowe$', views.twoje_so, name='twoje_so'),
    url(r'^edytuj-sesje-obiadowa/(?P<so_id>[\d]+)$', views.edytuj_so, name='edytuj_so'),
    url(r'^raport/(?P<so_id>[\d]+)$', views.raport, name='raport'),
    url(r'^twoje_zamowienia$', views.twoje_zamowienia, name='twoje_zamowienia'),
    url(r'^zamowienia/dodaj/(?P<so_id>[\d]+)$', views.zamow, name='zamow'),
    url(r'^zamowienie/(?P<z_id>[\d]+)$', views.zamowienie, name='zamowienie'),
    url(r'^zamowienie/(?P<z_id>[\d]+)/edytuj$', views.edytuj_zamowienie, name='edytuj_zamowienie'),
    url(r'^zamowienie/(?P<z_id>[\d]+)/usun$', views.usun_zamowienie, name='usun_zamowienie'),
    url(r'^historia$', views.historia, name='historia')
]
