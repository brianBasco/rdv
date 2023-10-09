
import json
from datetime import datetime

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

from .forms import (Add_Participant_Form, ContactForm, HTMXParticipantForm,
                    Liste_contactsForm, ParticipantForm, RdvForm)
from .models import Contact, Deuldou, Liste_contacts, Participant, Tag, User

# ------------------- Paramètres de config -----------------------

ERREUR = "Une erreur est survenue..."
PERMISSION = "Permission non accordée"
TEMPLATE_INFOS = "layout/partials/infos.html"

#Pages :
MAIN = 'users/0_main'
GESTION_RDV = 'users/1_gestion_rdv'
CONTACTS = 'users/2_contacts'
PROFIL = 'users/3_profil'

# ------------------- Create your views here ---------------------

# ------------------- Vues de test ---------------------
def test(request: HttpRequest):
    username:str = request.user.username
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

    #response = HttpResponse(mimetype="text/calendar")
    #response['Content-Disposition'] = 'attachment; filename=%s.ics' % event.slug
    f1 = ContentFile(cal.to_ical())
    response = HttpResponse(f1,headers={"Content-Type": "text/calendar","Content-Disposition": 'attachment; filename="foo.ics"',},)
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


# ------------------- Vues des components ---------------------
def rdv_template(request: HttpRequest):
    form: RdvForm = RdvForm()
    return render(request,"components/RdvForm.html", {"form": form})


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
            messages.add_message(request, messages.ERROR, "Erreur lors de la connexion - Identifiants incorrects")
            return render(request, 'registration/login.html')

    return render(request, 'registration/login.html')

def registration(request: HttpRequest):
    if request.method == "POST":
            email = request.POST['email']
            password = request.POST['password']
            nom = request.POST['nom']
           
            if User.objects.filter(email=email).exists():
                messages.add_message(request, messages.ERROR,'Cet utilisateur existe déjà')

            elif __check_passwordValidation(request, password):
                user = User.objects.create_user(username=email, email=email, password=password, first_name=nom)
                login(request, user)
                return redirect('home') 
    return render(request, 'registration/register.html')



@login_required
def logout_view(request: HttpRequest):
    messages.add_message(request, messages.INFO,'Déconnexion ! @Bientôt')
    logout(request)
    # Redirect to a success page.    
    return redirect('login')

# ------------------- Fin des Vues de Connexion/Déconnexion  ---------------------


# ------------------- Vues du profil  ---------------------
@login_required
def profil_view(request: HttpRequest):
    return render(request, 'users/3_profil/profil.html')


@login_required
def modifier_password(request: HttpRequest):
    user: User = request.user
    if request.method == 'POST':
        password = request.POST["password"]
        password2 = request.POST["password2"]
        if not password == password2:
            messages.add_message(request, messages.ERROR,'Les mots de passe ne correspondent pas')
        else :
            user.set_password(password)
            user.save()
            login(request, user)
            messages.add_message(request, messages.SUCCESS,"Your password has been changed")
            return redirect('home')
        
    return render(request, 'users/3_profil/modifier_password.html')

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
    participations = Participant.objects.filter(email=request.user.email).order_by('rdv__jour')
    rdvs = [r.rdv for r in participations]
    response = render(request, MAIN + '/partials/liste_rdvs.html', {'rdvs': rdvs})
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
        deuldou: Deuldou = form.save(commit=False)
        deuldou.created_by = request.user
        deuldou.save()
        participation: Participant = Participant(email=user.email, rdv=deuldou, nom=user.first_name)
        if request.POST.get('createur_participe'):
            participation.statut=Participant.PRESENT
        else:
            participation.statut=Participant.ABSENT
        participation.save()
        response: HttpResponse = HttpResponse("Votre rdv a été créé !")
        response["HX-Trigger"] = 'updateRDV'
        return response
    return render(request, 'components/RdvForm.html', {'form': form}) 


@login_required
def htmx_updateParticipant(request: HttpRequest, id_participant: int):
    """
    Sécurité : à tester !
    Retourne le Participant de ce RDV
    """
    context = dict()
    errors = set()
    try:
        #participant = Participant.objects.get(pk=id_participant)
        participant = Participant.get_for_user(id_participant,request.user)
    except ObjectDoesNotExist :
        errors.add(ERREUR)
        context['errors'] = errors
        return render(request, TEMPLATE_INFOS, context= context)
    except PermissionDenied:
        errors.add(PERMISSION)
        context['errors'] = errors
        return render(request, TEMPLATE_INFOS, context= context)
    # checker s'il s'agit bien d'un User autorisé
    #if request.user.email != participant.email:
    #    #return HttpResponse(PERMISSION)
    #    errors.add(PERMISSION)
    form = HTMXParticipantForm(instance=participant)
    if request.method == 'POST':
        form = HTMXParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            rdv:int = participant.rdv.id
            context['success'] = {"Votre participation a été mise à jour"}
            # retourne un Event dans le Header pour le HTMX
            #response = HttpResponse("Votre participation a été mise à jour")
            response = render(request, TEMPLATE_INFOS, context= context)
            response["HX-Trigger"] = 'updateParticipants_' + str(rdv)
            return response
        else:
            errors.add(ERREUR + " le formulaire n'est pas valide")
            context['errors'] = errors
            return render(request, TEMPLATE_INFOS, context= context)
    
    return render(request, "users/0_main/partials/participantForm.html", {'form': form, 'id_participant': id_participant})
    # retourner le formulaire s'il n'y a pas d'erreurs, sinon la liste des erreurs :
    #if len(errors) == 0:
    #    return render(request, "users/0_main/partials/participantForm.html", {'form': form, 'id_participant': id_participant})
    #else:
    #    context['errors'] = errors
    #    return render(request, TEMPLATE_INFOS, context= context)


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
    except Exception :
        return HttpResponse(PERMISSION)
    participants = Participant.objects.filter(rdv=rdv)
    # Ajout du nombre de participants :
    #nbparticipants = Participant.objects.filter(Q(statut=Participant.PRESENT) | Q(statut=Participant.RETARD), rdv=rdv).count()
    nbparticipants = participants.filter(Q(statut=Participant.PRESENT) | Q(statut=Participant.RETARD), rdv=rdv).count()
    inscrits = 'inscrits'
    if nbparticipants < 2:
        inscrits = 'inscrit'
    nbre = "{} {}".format(str(nbparticipants), inscrits)
    return render(request, "users/0_main/partials/liste_participants.html", {'id_rdv': id_rdv, 'participants': participants, 'nbre':nbre})

# ------------------- Fin des vues de la page principale  ---------------------
        
# ------------------- Vues de gestion des CONTACTS  ---------------------

@login_required
def contacts_view(request: HttpRequest):
    #contacts = ContactService.get_Contacts(request.user)
    user:User = request.user
    contacts: list[Contact] = user.contacts.all()
    return render(request, "users/2_contacts/index.html", {'contacts': contacts})


@login_required
def add_liste_contact_view(request: HttpRequest):
    if request.method == "POST":
        form = Liste_contactsForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["user"] != request.user:
                raise PermissionDenied
            form.save()
            messages.add_message(request, messages.SUCCESS, "Nouvelle liste de contacts ajoutée")
            return redirect('home')
        else:
            return render(request, "users/liste_contacts/add.html", {'form': form})

    form = Liste_contactsForm(instance=Liste_contacts(user=request.user))
    return render(request, "users/liste_contacts/add.html", {'form': form})


@login_required
def htmx_addContact(request: HttpRequest):
    """
    Ajoute le contact au User (User basé sur la session) et retourne le signal pour MAJ Htmx
    """
    user: User = request.user
    if request.method == "GET":
        #form: ContactForm = ContactForm(initial={'user': user})
        form: ContactForm = ContactForm()
        return render(request, "users/2_contacts/partials/contactForm.html", {'form': form})
    if request.method == "POST":
        contact: Contact = Contact(user=request.user)
        form: ContactForm = ContactForm(request.POST, instance=contact)
        if form.is_valid():
            form.save()
            #messages.add_message(request, messages.SUCCESS, "Le contact a été ajouté")

        else:
            pass
            #print(form.errors)
            # A faire : récupérer les erreurs du formulaire
            #messages.add_message(request, messages.ERROR, "vous ne pouvez pas enregistrer cet utilisateur !")
        #return redirect('contacts')
        response = HttpResponse()
        response.headers["HX-Trigger"] = "addContact"
        return response



# ------------------- Vues de gestion des RDV  ---------------------

@login_required
def gerer_rdvs(request: HttpRequest):
    """
    Sécurité: OK
    Retourne les RDV créés par le USER
    Fonctionnel
    """
    rdvs: list[Deuldou] = Deuldou.objects.filter(created_by=request.user)
    return render(request, "users/1_gestion_rdv/index.html", {'rdvs': rdvs})


@login_required
def modifier_rdv(request: HttpRequest, id: int):
    """
    Sécurité : à tester
    Retourne un RDV créé par le USER pour modification
    Renvoyer les erreurs sur le formulaire si formulaire non valide
    NON FONCTIONNEL
    """
    try:
        rdv:Deuldou = Deuldou.get_for_user(rdv_id=id, user=request.user)
    except ObjectDoesNotExist :
        return HttpResponse(ERREUR)
    except PermissionDenied :
        return HttpResponse(PERMISSION)
    form = RdvForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        form.save()
        response = HttpResponse("Le Rdv a été modifié !")
        response["HX-trigger"] = "rdv_updated"
        return response
    context = {'form': form, 'rdv_id': id}
    return render(request, 'users/1_gestion_rdv/update/index.html', context=context)

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
            rdv: Deuldou = Deuldou.get_for_user(rdv_id=rdv_id, user=request.user)
        except ObjectDoesNotExist:
            context['errors'] = {ERREUR}
        except PermissionDenied:
            context['errors'] = {PERMISSION}
        else:
            rdv.delete()
            context['success'] = {'Le Rendez-Vous a été supprimé'}
            response = render(request, TEMPLATE_INFOS, context)
            response['HX-trigger'] = json.dumps({"rdvDeleted": str(rdv_id)})
            return response
        return render(request, TEMPLATE_INFOS, context)
        


# Méthode à reprendre
@login_required
def x_gestion_getParticipants(request: HttpRequest, rdv_id:int):
    '''
    Sécurité : à tester
    retourne la liste des participants à un Rdv créé par le USER \n,
    Fonctionnel
    '''
    try:
        rdv: Deuldou = Deuldou.get_for_user(rdv_id=rdv_id,user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse(ERREUR)
    except PermissionDenied :
        return HttpResponse(PERMISSION)
    participants = Participant.objects.filter(rdv=rdv)
    return render(request, "users/1_gestion_rdv/partials/participants.html", {'participants': participants})


@login_required
def x_deleteParticipant(request: HttpRequest, id: int):
    '''
    Supprime le participant d'un Rdv, avec méthode DELETE \n
    Sécurité : à tester  \n
    Risque de suppression d'un Participant d'un autre User
    Vérifier que le Participant appartient à un Rdv du User.
    Fonctionnel
    '''
    if request.method == "DELETE":
        context = {}
        # Sécurité :
        try:
            participant: Participant = Participant.objects.get(pk=id)
        except ObjectDoesNotExist:
            context['errors'] = {ERREUR}
        else:
            try:
                rdv: Deuldou = Deuldou.get_for_user(rdv_id=participant.rdv.id, user=request.user)
            except ObjectDoesNotExist :
                context['errors'] = {ERREUR}
            except PermissionDenied:
                context['errors'] = {PERMISSION}
            else:
                participant.delete()
                context['success'] = {"Le participant a été supprimé"}
                response = render(request, 'layout/partials/infos.html', context)
                response['HX-Trigger'] = 'participantDeleted_' + str(rdv.id)
                return response
        return render(request, 'layout/partials/infos.html', context)
        
    
@login_required
def x_addParticipant(request: HttpRequest, rdv_id: int):
    """
    Sécurité : à tester
    Ajoute un participant à un RDV créé par le USER
    NON FONCTIONNEL
    """
    context = {}
    try:
        rdv: Deuldou = Deuldou.get_for_user(rdv_id=rdv_id, user=request.user)
    except ObjectDoesNotExist:
        return HttpResponse(ERREUR)
    except PermissionDenied:
        return HttpResponse(PERMISSION)
    form = ParticipantForm(request.POST or None)
    if request.method == "POST":
        if form.is_valid():
            #form = ParticipantForm(request.POST)
            #context = {}
            #if form.is_valid():
            print("form is valid")
            form.save()
            context['success'] = {'Participant ajouté !'}
            response = render(request, 'layout/partials/infos.html', context)
            response['HX-Trigger'] = 'participantAdded_' + str(rdv_id)
            return response
        else :
            print("form is NOT valid")
            print(form)
            context['errors'] = {"Le participant n'a pas pu être ajouté !"}
            return render(request, 'layout/partials/infos.html', context)
    #deuldou: Deuldou = Deuldou.objects.get(pk=rdv_id)
    # Il faut instancier avant le formulaire pour récupérer la value du rdv pour le formulaire (dans la vue)
    form = ParticipantForm(instance=Participant(rdv=rdv))
    context = {"form": form, "rdv_id": rdv_id}
    return render(request, 'users/1_gestion_rdv/partials/modalParticipant.html', context=context)


# ------------------- Fin des Vues de gestion des RDV  ---------------------

# ------------------- Fin des Vues de l'application  ---------------------


def __check_passwordValidation(request: HttpRequest, password: str):
    validators = [MinimumLengthValidator, NumericPasswordValidator ]
    try:
        for validator in validators:
            validator().validate(password)
        return True
    except ValidationError as e:
            messages.add_message(request, messages.ERROR,str(e))
            return False

