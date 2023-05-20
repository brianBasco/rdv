
from datetime import datetime

import pytz
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.password_validation import (MinimumLengthValidator,
                                                     NumericPasswordValidator)
from django.core.exceptions import PermissionDenied
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

from .forms import (Add_Participant_Form, ContactForm, Create_Rdv_Form,
                    HTMXParticipantForm, Liste_contactsForm, ParticipantForm)
from .models import (Contact, Deuldou, Invite, Liste_contacts, Participant,
                     Tag, User)
from .services import (ContactService, DeuldouService, ParticipantService,
                       UserService)

# ------------------- Paramètres de config -----------------------

ERREUR = "Une erreur est survenue..."
PERMISSION = "Permission non accordée"

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
        

# ------------------- Fin des vues de test ---------------------


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
           
            if User.objects.filter(email=email).exists():
                messages.add_message(request, messages.ERROR,'Cet utilisateur existe déjà')

            elif __check_passwordValidation(request, password):
                user = User.objects.create_user(username=email, email=email, password=password, first_name="Moi !")
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
    return render(request, 'users/profil/profil.html')


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
        
    return render(request, 'users/profil/modifier_password.html')

# ------------------- Vues de L'application  ---------------------
"""
@login_required
def home(request: HttpRequest):
    rdvs: list[Deuldou] = UserService.get_Deuldous(request.user)
    liste_rdvs = list()
    for rdv in rdvs:
        dictionnaire = {}
        dictionnaire['rdv'] = rdv
        dictionnaire['participants'] = rdv.participants.all()
        liste_rdvs.append(dictionnaire)
    return render(request, 'users/index.html', {'liste_rdvs': liste_rdvs})
"""

@login_required
def home(request: HttpRequest):
    """
    Retourne la liste des RDV où le User participe\n
    Classement des participations dans l'ordre ascendant
    """
    participations = Participant.objects.filter(email=request.user.email).order_by('rdv__jour')
    rdvs = [r.rdv for r in participations]
    response = render(request, 'users/index.html', {'rdvs': rdvs})
    response.headers['HX-Trigger'] = 'getParticipants'
    #return render(request, 'users/index.html', {'rdvs': rdvs})
    return response

@login_required
def creer_rdv(request: HttpRequest):
    user: User = request.user
    if request.method == 'POST':
        form = Create_Rdv_Form(request.POST)
        if form.is_valid():
            print("form is valid")
            #deuldou: Deuldou = DeuldouService.create_Deuldou_form(user, form)
            deuldou: Deuldou = UserService.create_Deuldou(user,form)
            # Si le créateur participe aussi au Deuldou
            if form.cleaned_data['createur_participe']:
                UserService.participate(user, deuldou)
                #ParticipantService.ajouter_Participant(user.email,user.first_name,deuldou)
            messages.add_message(request, messages.SUCCESS, "Votre rendez-vous a été créé avec succès !")    
            return redirect('home')
        else:
            messages.add_message(request, messages.ERROR, "Le Rendez-vous n'a pas pu être créé !")              
    form: Create_Rdv_Form = Create_Rdv_Form()
    return render(request, "users/rdv/create_rdv_form.html", {'form': form})

@login_required
def ajouter_participant_rdv_view(request: HttpRequest, rdv_id:int):
    deuldou: Deuldou = UserService.get_Deuldou(rdv_id, request.user)
    form = ParticipantForm(instance=Participant(rdv=deuldou))

    if request.method == "POST" :
        form = ParticipantForm(request.POST)
        if form.is_valid():
            """ Vérif de sécu :
            Le formulaire envoyé doit correspondre au même Rdv appelé
            """
            if form.cleaned_data["rdv"] != deuldou:
                raise PermissionDenied
            form.save()
            messages.add_message(request, messages.SUCCESS, "un participant ajouté !")
            #Service USer mail ->
            return redirect('home')
    
    return render(request, 'users/rdv/ajouter_participant_rdv.html', {"form": form})


@login_required
def htmx_updateParticipant(request: HttpRequest, id_participant: int):
    """ Retourner le Participant de ce RDV """
    try:
        participant = Participant.objects.get(pk=id_participant)
    except Exception as e:
        return HttpResponse(ERREUR)
    # checker s'il s'agit bien d'un User autorisé
    if request.user.email != participant.email:
        return HttpResponse(PERMISSION)
    form = HTMXParticipantForm(instance=participant)
    if request.method == 'POST':
        form = HTMXParticipantForm(request.POST, instance=participant)
        if form.is_valid():
            form.save()
            # retourne un Event dans le Header pour le HTMX
            response = HttpResponse("Votre participation a été mise à jour")
            response.headers["HX-Trigger"] = "updateParticipant"
            return response
    return render(request, "users/htmx/participantForm.html", {'form': form, 'id_participant': id_participant})

@login_required
def htmx_getParticipants(request: HttpRequest, id_rdv: int):
    """ Retourne les participants à un RDV """
    try:
        rdv = Deuldou.objects.get(pk=id_rdv)
    except Exception:
        return HttpResponse(ERREUR)
    # Sécurité : le User qui demande ce RDV participe t-il à ce RDV ? S'il participe il doit donc avoir un participation correspondant à son email et au RDV
    try:
        Participant.objects.get(rdv=rdv, email=request.user.email)
    except Exception as e:
        return HttpResponse(PERMISSION)
    participants = Participant.objects.filter(rdv=rdv)
    return render(request, "users/htmx/liste_participants.html", {'id_rdv': id_rdv, 'participants': participants})

    
@login_required
def htmx_getNombreParticipants(request: HttpRequest, id_rdv: int):
    """ Retourne le nombre de participants présents et en retard à un RDV """
    try:
        rdv = Deuldou.objects.get(pk=id_rdv)
    except Exception as e:
        return HttpResponse(ERREUR)
    # Sécurité : le User qui demande ce RDV participe t-il à ce RDV ? S'il participe il doit donc avoir un participation correspondant à son email et au RDV
    try:
        Participant.objects.get(rdv=rdv, email=request.user.email)
    except Exception as e:
        return HttpResponse(PERMISSION)
    nbparticipants = Participant.objects.filter(Q(statut=Participant.PRESENT) | Q(statut=Participant.RETARD), rdv=rdv).count()
    inscrits = 'inscrits'
    if nbparticipants < 2:
        inscrits = 'inscrit'
    return HttpResponse("{} {}".format(str(nbparticipants), inscrits))

"""
def creer_hashtag(request):
    user = request.user
    if request.method == 'POST':
        Tag.objects.create(user=user, nom=request.POST["nom"])
    return redirect('home')


def filtrer_par_hashtag(request):
    # Permet de filtrer l'affichage des invitations suivant leur étiquette
    if request.method == "POST":
        pass
    return redirect('home')

"""


# ------------------- Fin des Vues des ajouts de Participants à un RDV  ---------------------

# ------------------- Vues de gestion des CONTACTS  ---------------------

@login_required
def contacts_view(request: HttpRequest):
    contacts = ContactService.get_Contacts(request.user)
    return render(request, "users/contacts/index.html", {'contacts': contacts})

@login_required
def add_contact_view(request: HttpRequest):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            if form.cleaned_data["user"] != request.user:
                raise PermissionDenied
            form.save()
            messages.add_message(request, messages.SUCCESS, "Contact ajouté")
            return redirect('home')
        else:
            return render(request, "users/contacts/add.html", {'form': form})

    form = ContactForm(instance=Contact(user=request.user))
    return render(request, "users/contacts/add.html", {'form': form})

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

# ------------------- Vues de gestion des RDV  ---------------------

@login_required
def gerer_rdvs(request: HttpRequest):
    rdvs: list[Deuldou] = UserService.get_Deuldous(request.user)
    liste_rdvs = list()
    for rdv in rdvs:
        dictionnaire = {}
        dictionnaire['rdv'] = rdv
        dictionnaire['participants'] = rdv.participants.all()
        liste_rdvs.append(dictionnaire)
    return render(request, "users/rdv/liste.html", {'liste_rdvs': liste_rdvs})

@login_required
def htmx_get_contacts(request: HttpRequest, id_rdv: int):
    """ Retourner les contacts qui ne participent pas encore à ce RDV """
    if request.method == 'POST':
        rdv = get_object_or_404(Deuldou, pk=id_rdv)
        participants = Participant.objects.filter(rdv=rdv)
        emails = [p.email for p in participants]
        contacts = Contact.objects.filter(user=request.user).exclude(email__in=emails)
        print(contacts)
        return render(request, "users/rdv/htmx/contacts.html", {'items': contacts, 'id_rdv': id_rdv})
    
def htmx_add_contact(request: HttpRequest, id_rdv: int, id_contact: int):
    """
    Ajouter le contact comme participant\n
    Retourner les contacts qui ne participent pas encore à ce RDV
    """
    if request.method == 'POST':
        contact = get_object_or_404(Contact, pk=id_contact)
        rdv = get_object_or_404(Deuldou, pk=id_rdv)
        try:
            ParticipantService.ajouter_Participant(contact.email, contact.nom, rdv=rdv)
        except:
            return HttpResponse("Une erreur est survenue lors de l'ajout du Contact")
        return htmx_get_contacts(request,id_rdv)

@login_required
def modifier_rdv(request: HttpRequest, id: int):
    pass

@login_required
def supprimer_rdv(request: HttpRequest, id: int):
    pass

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

