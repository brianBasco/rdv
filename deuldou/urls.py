from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    #path('', views.connexion, name="connexion"),
    path('', views.home, name="home"),
    
    path('login', views.login_view, name="login"),
    path('registration', views.registration, name="registration"),
    path('modifier_password', views.modifier_password, name="modifier_password"),
    path('logout', views.logout_view, name="logout"),

    path('profil', views.profil_view, name="profil"),

    path('contacts', views.contacts_view, name="contacts"),
    #path('add_contact', views.add_contact_view, name="add_contact"),
    path('add_liste_contact', views.add_liste_contact_view, name="add_liste_contact"),

    # fonctions de la page 0 :
    path('x_addRdv', views.x_addRdv, name="x_addRdv"),
    path('x_getRdvs', views.x_getRdvs, name="x_getRdvs"),
    path('htmx_updateParticipant/<int:id_participant>', views.htmx_updateParticipant, name="htmx_updateParticipant"),
    path('htmx_getParticipants/<int:id_rdv>', views.htmx_getParticipants, name="htmx_getParticipants"),

    # fonctions de la page 1 :
    path('gerer_rdvs',views.gerer_rdvs , name="gerer_rdvs"), # Secu OK
    path('modifier_rdv/<int:id>',views.modifier_rdv , name="modifier_rdv"),
    path('deleteRdv/<int:rdv_id>',views.x_deleteRdv , name="x_deleteRdv"),
    path('x_addParticipant/<int:rdv_id>',views.x_addParticipant, name="x_addParticipant"),
    path('x_gestion_getParticipants/<int:rdv_id>',views.x_gestion_getParticipants, name="x_gestion_getParticipants"),
    path('x_deleteParticipant/<int:id>',views.x_deleteParticipant, name="x_deleteParticipant"),

    # vue des tests
    path('test', views.test, name="test"),
    path('test_download', views.test_download, name="test_download"),
    path('test_oob', views.test_oob, name="test_oob"),
    path('test_index', views.test_index, name="test_index"),
    path('htmx_addContact', views.htmx_addContact, name="htmx_addContact"),
    
    # Vue des components
    path('rdv_template', views.rdv_template, name="rdv_template"),
    
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name="password_reset"),
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name="password_reset_done"),
    path("password_reset_confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name="password_reset_confirm"),
    path("password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name="password_reset_complete"),
    
]

#handler404 = 'mysite.views.my_custom_page_not_found_view'
