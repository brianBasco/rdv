from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from . import views

urlpatterns = [
    #path('', views.connexion, name="connexion"),
    path('', views.home, name="home"),
    path('creer_rdv', views.creer_rdv, name="creer_rdv"),
    path('login', views.login_view, name="login"),
    path('registration', views.registration, name="registration"),
    path('modifier_password', views.modifier_password, name="modifier_password"),
    path('logout', views.logout_view, name="logout"),

    path('profil', views.profil_view, name="profil"),

    path('contacts', views.contacts_view, name="contacts"),
    path('add_contact', views.add_contact_view, name="add_contact"),
    path('add_liste_contact', views.add_liste_contact_view, name="add_liste_contact"),
    

    path('test', views.test, name="test"),
    path('test_download', views.test_download, name="test_download"),
    #path('htmx_get_contacts/<int:id_rdv>', views.htmx_get_contacts, name="htmx_get_contacts"),
    #path('htmx_add_contact/<int:id_rdv>/<int:id_contact>', views.htmx_add_contact, name="htmx_add_contact"),
    path('htmx_getContacts', views.htmx_getContacts, name="htmx_getContacts"),
    path('htmx_addContact', views.htmx_addContact, name="htmx_addContact"),
    
    

    path('gerer_rdvs',views.gerer_rdvs , name="gerer_rdvs"),
    path('modifier_rdv/<int:id>',views.modifier_rdv , name="modifier_rdv"),
    path('supprimer_rdv/<int:id>',views.supprimer_rdv , name="supprimer_rdv"),
    path('ajouter_participant_rdv/<int:rdv_id>',views.ajouter_participant_rdv_view , name="ajouter_participant_rdv"),
    # HTMX
    path('htmx_updateParticipant/<int:id_participant>', views.htmx_updateParticipant, name="htmx_updateParticipant"),
    path('htmx_getParticipants/<int:id_rdv>', views.htmx_getParticipants, name="htmx_getParticipants"),
    path('htmx_getNombreParticipants/<int:id_rdv>', views.htmx_getNombreParticipants, name="htmx_getNombreParticipants"),

    

    

    #path("change-password/", auth_views.PasswordChangeView.as_view()),
    #path("change-password-done/", auth_views.PasswordChangeDoneView.as_view()),
    path("password_reset/", auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name="password_reset"),
    path("password_reset_done/", auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name="password_reset_done"),
    path("password_reset_confirm/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name="password_reset_confirm"),
    path("password_reset_complete/", auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name="password_reset_complete"),
    
    
    
]

#handler404 = 'mysite.views.my_custom_page_not_found_view'
