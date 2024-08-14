
import json
from datetime import datetime
from django.forms import formset_factory

import pytz
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import (MinimumLengthValidator,
                                                     NumericPasswordValidator)
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.core.files.base import ContentFile
from django.db.models import Q
from django.forms import ValidationError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView
from icalendar import Calendar, Event
from ics import Calendar as Cal
from ics import Event as Ev
from pwgen import pwgen

from .forms import ContactForm, ListeContactsForm, ParticipantForm, RdvForm, SelectContactForm, UpdateParticipantForm
from .models import Contact, Deuldou, ListeContacts, ListeContacts, Participant, Tag, User

# ------------------- Paramètres de config -----------------------

ERREUR = "Une erreur est survenue..."
PERMISSION = "Permission non accordée"
TEMPLATE_INFOS = "layout/partials/infos.html"

# Pages :
MAIN = 'users/0_main'
GESTION_RDV = 'users/1_gestion_rdv'
CONTACTS = 'users/2_contacts'
PROFIL = 'users/3_profil'

# ------------------- Create your views here ---------------------

# ------------------- Vues de test ---------------------


def test(request: HttpRequest):
    username: str = request.user.username
    print("ok on est là")
    return HttpResponse(str(username))


def test_hashtag(request, nom):
    tag = Tag.objects.get(nom=nom)
    reponse = f'<h1>{tag.nom}</h1>'
    return HttpResponse(reponse)


def test_download(request):
    # Code fonctionnel avec icalendar :
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//example.com//')
    cal.add('version', '2.0')

    event = Event()
    event.add('name', 'Awesome Meeting')
    event.add('description', 'Define the roadmap of our awesome project')
    event.add('dtstart', datetime(2022, 1, 25, 8, 0, 0, tzinfo=pytz.utc))
    event.add('dtend', datetime(2022, 1, 25, 10, 0, 0, tzinfo=pytz.utc))
    cal.add_component(event)

    # response = HttpResponse(mimetype="text/calendar")
    # response['Content-Disposition'] = 'attachment; filename=%s.ics' % event.slug
    f1 = ContentFile(cal.to_ical())
    response = HttpResponse(f1, headers={
                            "Content-Type": "text/calendar", "Content-Disposition": 'attachment; filename="foo.ics"', },)
    return response


def test_index(request):
    return render(request, 'TEST/test.html')


def test_oob(request):
    context = {}
    context['results'] = ["un", "deux", "trois"]
    context['success'] = {"OK !", "ça fonctione !"}
    context['errors'] = {"Erreur !"}
    return render(request, 'TEST/partial.html', context=context)


# ------------------- Fin des vues de test ---------------------

# ------------------- Fonction de calendrier -------------------
def download_cal(request, rdv_id: int):
    rdv = Deuldou.get_for_user(rdv_id=rdv_id,user=request.user)
    # Code fonctionnel avec icalendar :
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//example.com//')
    cal.add('version', '2.0')

    event = Event()
    event.add('name', rdv.nom)
    event.add('description', rdv.lieu)
    #event.add('dtstart', datetime(2022, 1, 25, 8, 0, 0, tzinfo=pytz.utc))
    #print(datetime.strptime(rdv.heure_debut, '%H:%M:%S'))
    event.add('dtstart', rdv.heure_debut)
    print(event)
    # Affichage de la date de début de l'événement
    start_date = event.get('dtstart').dt
    print("Date de début de l'événement :", start_date)
    event.add('dtend', rdv.heure_fin)
    cal.add_component(event)

    # response = HttpResponse(mimetype="text/calendar")
    # response['Content-Disposition'] = 'attachment; filename=%s.ics' % event.slug
    f1 = ContentFile(cal.to_ical())
    response = HttpResponse(f1, headers={
                            "Content-Type": "text/calendar", "Content-Disposition": "attachment; filename={}.ics".format(rdv.nom),},)
    return response


# ------------------- Vues des components ---------------------
def rdv_template(request: HttpRequest):
    form: RdvForm = RdvForm()
    return render(request, "components/Rdv/RdvForm.html", {"form": form})


# ------------------- Fin des vues des components ---------------------

# ------------------- Vues de Connexion/Déconnexion  ---------------------
def login_view(request: HttpRequest):

    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request, username=email, password=password)
        if user is not None:
            print("user identifié !!")
            # Redirect to a success page.
            login(request, user)
            return redirect('home')

        else:
            messages.add_message(
                request, messages.ERROR, "Erreur lors de la connexion - Identifiants incorrects")
            return render(request, 'registration/login.html')

    return render(request, 'registration/login.html')


def registration(request: HttpRequest):
    if request.method == "POST":
        email = request.POST['email']
        password = request.POST['password']
        nom = request.POST['nom']

        if User.objects.filter(email=email).exists():
            messages.add_message(request, messages.ERROR,
                                 'Cet utilisateur existe déjà')

        elif __check_passwordValidation(request, password):
            user = User.objects.create_user(
                username=email, email=email, password=password, first_name=nom)
            login(request, user)
            return redirect('home')
    return render(request, 'registration/register.html')


@login_required
def logout_view(request: HttpRequest):
    messages.add_message(request, messages.INFO, 'Déconnexion ! @Bientôt')
    logout(request)
    # Redirect to a success page.
    return redirect('login')

# ------------------- Fin des Vues de Connexion/Déconnexion  ---------------------


# ------------------- Vues du profil  ---------------------

@login_required
def modifier_password(request: HttpRequest):
    user: User = request.user
    if request.method == 'POST':
        password = request.POST["password"]
        password2 = request.POST["password2"]
        if not password == password2:
            messages.add_message(request, messages.ERROR,
                                 'Les mots de passe ne correspondent pas')
        else:
            user.set_password(password)
            user.save()
            login(request, user)
            messages.add_message(request, messages.SUCCESS,
                                 "Your password has been changed")
            return redirect('home')

    return render(request, 'users/3_profil/modifier_password.html')

@login_required
def x_get_profil(request: HttpRequest):
    return render(request, 'components/Profil/ProfilModal.html')

# ------------------- Vues de L'application  ---------------------


@login_required
def home(request: HttpRequest):
    """
    Retourne la liste des RDV où le User participe\n
    Classement des participations dans l'ordre ascendant
    """
    return render(request, MAIN + '/index.html')


@login_required
def x_getRdvs(request: HttpRequest):
    """
    Sécurité : OK
    Retourne la liste des RDV où le User participe\n
    Classement des participations dans l'ordre ascendant
    """
    participations = Participant.objects.filter(
        email=request.user.email).order_by('rdv__jour')
    rdvs = [r.rdv for r in participations]
    response = render(
        request, MAIN + '/partials/liste_rdvs.html', {'rdvs': rdvs})
    response.headers['HX-Trigger'] = 'getParticipants'
    return response


@login_required
def x_addRdv(request: HttpRequest):
    """ 
    Sécurité : OK
    retourne le formulaire vide si GET
    """
    user: User = request.user
    form: RdvForm = RdvForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.instance.created_by = request.user
        rdv: Deuldou = form.save()
        participation: Participant = Participant(
            email=user.email, rdv=rdv, nom=user.first_name)
        if request.POST.get('createur_participe'):
            participation.statut = Participant.PRESENT
        else:
            participation.statut = Participant.ABSENT
        participation.save()
        response: HttpResponse = HttpResponse('<div class="alert alert-success" role="alert">Votre rdv a été créé !</div>')
        response["HX-Trigger"] = 'updateRDV'
        return response
    return render(request, 'components/Rdv/RdvModal.html', {'form': form})


@login_required
def htmx_updateParticipant(request: HttpRequest, id_participant: int):
    """
    Sécurité : à tester !
    Retourne le Participant de ce RDV
    """
    try:
        # participant = Participant.objects.get(pk=id_participant)
        participant: Participant = Participant.get_for_user(id_participant, request.user)
        #participant: Participant = Participant.get_for_user(0, request.user)
    except:
        return render(request, 'components/Participant/UpdateParticipantModalInfos.html', {'error': ERREUR})
    form = UpdateParticipantForm(instance=participant)
    if request.method == 'POST':
        form = UpdateParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            rdv: int = participant.rdv.id
            #response = render(request, 'components/Modal/formInfos.html', {'success': "Votre participation a été mise à jour"})
            response = render(request, 'components/Participant/UpdateParticipantModalInfos.html', {'success': "Votre participation a été mise à jour"})
            response["HX-Trigger"] = 'updateParticipants_' + str(rdv)
            return response
    # GET méthode et/ou Formulaire invalide
    return render(request, "components/Participant/UpdateParticipantModal.html", {'form': form, 'id_participant': id_participant})


@login_required
def htmx_getParticipants(request: HttpRequest, id_rdv: int):
    """
    Sécurité : à tester !!
    Retourne les participants à un RDV
    """
    try:
        rdv = Deuldou.objects.get(pk=id_rdv)
    except Exception:
        return HttpResponse(ERREUR)
    # Sécurité : le User qui demande ce RDV participe t-il à ce RDV ? S'il participe il doit donc avoir un participation correspondant à son email et au RDV
    try:
        Participant.objects.get(rdv=rdv, email=request.user.email)
    except Exception:
        return HttpResponse(PERMISSION)
    participants = Participant.objects.filter(rdv=rdv)
    # Ajout du nombre de participants :
    # nbparticipants = Participant.objects.filter(Q(statut=Participant.PRESENT) | Q(statut=Participant.RETARD), rdv=rdv).count()
    nbparticipants = participants.filter(Q(statut=Participant.PRESENT) | Q(
        statut=Participant.RETARD), rdv=rdv).count()
    inscrits = 'inscrits'
    if nbparticipants < 2:
        inscrits = 'inscrit'
    nbre = "{} {}".format(str(nbparticipants), inscrits)
    return render(request, "users/0_main/partials/liste_participants.html", {'id_rdv': id_rdv, 'participants': participants, 'nbre': nbre})

# ------------------- Fin des vues de la page principale  ---------------------

# ------------------- Vues de la page 2 - Gestion des CONTACTS  ---------------------


@login_required
def contacts_view(request: HttpRequest):
    return render(request, "users/2_contacts/index.html")


@login_required
def x_getContacts(request: HttpRequest):
    contacts: list[Contact] = request.user.contacts.all()
    return render(request, "users/2_contacts/partials/liste_contacts.html", {'contacts': contacts})


"""
@login_required
def add_liste_contact_view(request: HttpRequest):
    if request.method == "POST":
        form = Liste_contactsForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["user"] != request.user:
                raise PermissionDenied
            form.save()
            messages.add_message(request, messages.SUCCESS,
                                 "Nouvelle liste de contacts ajoutée")
            return redirect('home')
        else:
            return render(request, "users/liste_contacts/add.html", {'form': form})

    form = Liste_contactsForm(instance=Liste_contacts(user=request.user))
    return render(request, "users/liste_contacts/add.html", {'form': form})
"""


@login_required
def x_addContact(request: HttpRequest):
    """
    Sécurité : à tester
    Ajoute un Contact à un User
    NON FONCTIONNEL
    """
    if request.method == "POST":
        form: ContactForm = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            response = render(request, 'components/Contact/formInfos.html', {'success': 'Contact ajouté'})
            response.headers["HX-Trigger"] = "addContact"
            return response
    else:
        form: ContactForm = ContactForm(initial={'user': request.user})
    return render(request, "components/Contact/ContactForm.html", {'form': form})


@login_required
def x_updateContact(request: HttpRequest, contact_id:int):
    try:
        contact:Contact = Contact.get_for_user(pk=contact_id, user=request.user)
    except ObjectDoesNotExist:
        return render(request, "components/Contact/formInfos.html",  {'error':HttpResponse(ERREUR)})
    except PermissionDenied:
        return render(request, "components/Contact/formInfos.html",  {'error':HttpResponse(PERMISSION)})
    else:
        print(contact)
        form: ContactForm = ContactForm(instance=contact)
        print(form)
        if request.method == "POST":
            form: ContactForm = ContactForm(request.POST, instance=contact)
            if form.is_valid():
                form.save()
                response = render(request, "components/Contact/formInfos.html",  {'success': 'Contact modifié'})
                response.headers["HX-Trigger"] = "addContact"
                return response
        return render(request, "components/Contact/UpdateContactForm.html", {'form': form, 'contact_id': contact_id})
    

@login_required
def x_deleteContact(request: HttpRequest, contact_id: int):
    """
    Sécurité : à tester
    Supprimme un Contact créé par le USER
    Fonctionnel
    """
    if request.method == 'DELETE':
        try:
            contact: Contact = Contact.get_for_user(pk=contact_id, user=request.user)
        except ObjectDoesNotExist:
            return HttpResponse(ERREUR)
        except PermissionDenied:
            return HttpResponse(PERMISSION)
        else:
            contact.delete()
            return HttpResponse(status=200)

@login_required
def x_addListeContacts(request: HttpRequest):
    form:ListeContactsForm = ListeContactsForm(initial={'user': request.user})
    if request.method == 'POST':
        form:ListeContactsForm = ListeContactsForm(request.POST)
        print(form)
        if form.is_valid():
            print('form is valid')
            liste:ListeContacts = form.save()
            return HttpResponse(liste.__str__())
    return render(request, 'components/ListeContacts/form.html', {'form': form})

@login_required
def x_getListesContacts(request:HttpRequest):
    listes: ListeContacts = request.user.get_listes_contacts.all()
    return render(request, '{}/partials/liste_ListeContacts.html'.format(CONTACTS), {'listes': listes} )

@login_required
def x_updateListeContacts(request: HttpRequest):
    ...

@login_required
def x_deleteListeContacts(request: HttpRequest):
    ...

# ------------------- Vues de gestion des RDV  ---------------------

@login_required
def gerer_rdvs(request: HttpRequest):
    """
    Sécurité: OK
    Retourne les RDV créés par le USER
    Fonctionnel
    """
    # rdvs: list[Deuldou] = Deuldou.objects.filter(created_by=request.user).order_by('jour')
    # return render(request, "users/1_gestion_rdv/index.html", {'rdvs': rdvs})
    return render(request, "users/1_gestion_rdv/index.html")


@login_required
def x_get_rdvs(request: HttpRequest):
    """
    Sécurité: OK
    Retourne les RDV créés par le USER
    Fonctionnel
    """
    rdvs: list[Deuldou] = Deuldou.objects.filter(
        created_by=request.user).order_by('jour')
    response: HttpResponse = render(
        request, "users/1_gestion_rdv/partials/liste_rdvs.html", {'rdvs': rdvs})
    #response["HX-Trigger"] = "getParticipants"
    return response


@login_required
def x_update_rdv(request: HttpRequest, id: int):
    """
    Sécurité : à tester
    Retourne un RDV créé par le USER pour modification
    Renvoyer les erreurs sur le formulaire si formulaire non valide
    NON FONCTIONNEL
    """
    try:
        rdv: Deuldou = Deuldou.get_for_user(rdv_id=id, user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse(ERREUR)
    except PermissionDenied:
        return HttpResponse(PERMISSION)
    #form = RdvForm(request.POST or None)
    form = RdvForm(instance=rdv)
    if request.method == 'POST':
        form = RdvForm(data=request.POST,instance=rdv)
        if form.is_valid():
            form.save()
            response = HttpResponse("Le Rdv a été modifié !")
            response["HX-Trigger"] = "updateRDV"
            return response
    context = {'form': form, 'rdv_id': id}
    return render(request, 'components/Rdv/UpdateRdvModal.html', context=context)


@login_required
def x_deleteRdv(request: HttpRequest, rdv_id: int):
    """
    Sécurité : à tester
    Supprimme un RDV créé par le USER
    Fonctionnel
    """
    context = dict()
    if request.method == 'DELETE':
        try:
            rdv: Deuldou = Deuldou.get_for_user(
                rdv_id=rdv_id, user=request.user)
        except ObjectDoesNotExist:
            context['errors'] = {ERREUR}
        except PermissionDenied:
            context['errors'] = {PERMISSION}
        else:
            rdv.delete()
            context['success'] = {'Le Rendez-Vous a été supprimé'}
            response = render(request, 'users/1_gestion_rdv/partials/modalConfirmInfos.html', context)
            response['HX-trigger'] = json.dumps({"rdvDeleted": str(rdv_id)})
            return response
        return render(request, 'users/1_gestion_rdv/partials/modalConfirmInfos.html', context)


# Méthode à reprendre
@login_required
def x_gestion_getParticipants(request: HttpRequest, rdv_id: int):
    '''
    Sécurité : à tester
    retourne la liste des participants à un Rdv créé par le USER \n,
    Fonctionnel
    '''
    try:
        rdv: Deuldou = Deuldou.get_for_user(rdv_id=rdv_id, user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse(ERREUR)
    except PermissionDenied:
        return HttpResponse(PERMISSION)
    participants = Participant.objects.filter(rdv=rdv)
    return render(request, "users/1_gestion_rdv/partials/liste_participants.html", {'participants': participants})


@login_required
def x_deleteParticipant(request: HttpRequest, id: int):
    '''
    Supprime le participant d'un Rdv, avec méthode DELETE \n
    Sécurité : à tester  \n
    Risque de suppression d'un Participant d'un autre User
    Vérifier que le Participant appartient à un Rdv du User.
    Fonctionnel
    '''
    if request.method == "POST":
        context = {}
        # Sécurité :
        try:
            participant: Participant = Participant.objects.get(pk=id)
        except ObjectDoesNotExist:
            context['errors'] = {ERREUR}
        else:
            try:
                rdv: Deuldou = Deuldou.get_for_user(
                    rdv_id=participant.rdv.id, user=request.user)
            except ObjectDoesNotExist:
                context['errors'] = {ERREUR}
            except PermissionDenied:
                context['errors'] = {PERMISSION}
            else:
                participant.delete()
                context['success'] = {str.format("{} a été supprimé", participant.nom)}
                # response = render(request, 'layout/partials/infos.html', context)
                response = render(request, 'users/1_gestion_rdv/partials/modalConfirmInfos.html', context) 
                response['HX-Trigger'] = 'participantDeleted_' + str(rdv.id)
                return response
        return render(request, 'users/1_gestion_rdv/partials/modalConfirmInfos.html', context)


@login_required
def x_addParticipant(request: HttpRequest, rdv_id: int):
    """
    Ajoute un participant à un RDV créé par le USER
    Sécurité : testée
    FONCTIONNEL
    UI : 22/07/2024 vérifiée - Affichage Ok des erreurs et des succès dans le formulaire
    """
    context = {}
    try:
        rdv: Deuldou = Deuldou.get_for_user(rdv_id=rdv_id, user=request.user)
        #rdv: Deuldou = Deuldou.get_for_user(rdv_id=rdv_id, user=0)
    except ObjectDoesNotExist:
        return render(request, 'components/Participant/formInfosModal.html', {'error': ERREUR})
    except PermissionDenied:
        return render(request, 'components/Participant/formInfosModal.html', {'error': PERMISSION})
    form = ParticipantForm(initial={'rdv': rdv_id})
    if request.method == "POST":
        form = ParticipantForm(request.POST)
        if form.is_valid():
            participant: Participant = form.save()
            context['success'] = str.format('{} ajouté !', participant.nom)
            context["rdv_id"] = rdv_id
            response = render(request, 'components/Participant/formInfosModal.html', context)
            response['HX-Trigger'] = 'participantAdded_' + str(rdv_id)
            return response
        else:
            # Formulaire invalide : Renvoi du formulaire avec erreurs :
            return render(request, 'components/Participant/ParticipantModal.html', {"form": form, "rdv_id": rdv_id})
    # Méthode GET : Formulaire vierge :
    context = {"form": form, "rdv_id": rdv_id}
    return render(request, 'components/Participant/ParticipantModal.html', context=context)


@login_required
def x_selectContacts(request: HttpRequest, rdv_id:int):
    """
    Retourne la liste des contacts sans ceux déjà inscrits au RDV \n
    Ajoute les contacts sélectionnés comme participants
    """
    try:
        rdv:Deuldou = Deuldou.get_for_user(rdv_id=rdv_id, user=request.user)
    except:
        return HttpResponse(ERREUR)
    # récupérer les emails des participants au Rdv
    emails = [p.email for p in Participant.objects.filter(rdv=rdv_id)]
    # On enlève les participants pour déjà présents de la liste de contacts
    contacts = request.user.contacts.exclude(email__in=emails)
    ContactsFormSet = formset_factory(SelectContactForm, extra=0)
    formset = ContactsFormSet(initial=[{"nom": c.nom, "email": c.email} for c in contacts])
    print(len(formset))
    if request.method == "POST":
        formset = ContactsFormSet(request.POST)
        print(formset)
        if formset.is_valid():
            for form in formset:
                if form.cleaned_data['is_checked']:
                    nom = form.cleaned_data['nom']
                    email = form.cleaned_data['email']
                    Participant.objects.create(rdv=rdv, email=email, nom=nom)
            #response = render(request, 'components/Modal/formInfos.html',{'success':"Les contacts ont été ajoutés au Rendez-vous", 'button':'OK'}) 
            response = render(request, 'components/Contact/SelectContactsModalInfos.html',{'success':"Les contacts ont été ajoutés au Rendez-vous"}) 
            response['HX-Trigger'] = 'participantAdded_' + str(rdv_id)
            return response
    # Méthode GET : Retourne le formulaire initial
    context = {}
    context['rdv_id'] = rdv_id
    if len(formset) != 0:
        context['formset'] = formset
    return render(request, '{}/partials/liste_contacts.html'.format(GESTION_RDV), context=context)


# ------------------- Fin des Vues de gestion des RDV  ---------------------

# ------------------- Fin des Vues de l'application  ---------------------


def __check_passwordValidation(request: HttpRequest, password: str):
    validators = [MinimumLengthValidator, NumericPasswordValidator]
    try:
        for validator in validators:
            validator().validate(password)
        return True
    except ValidationError as e:
        messages.add_message(request, messages.ERROR, str(e))
        return False
