from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mail
from django.forms import ValidationError
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from pwgen import pwgen

from .forms import Create_Rdv_Form
from .models import Contact, Deuldou, Liste_contacts, Participant, Tag, User

# ------------------- Fonctions utilitaires  ---------------------
""" Utils de la V1 """
"""
def ajouterInvite(invite, deuldou):
    user = User.objects.get(username=invite.nom)
    # return Participation.objects.create(user=user, deuldou=deuldou)


def ajouterListeInvites(invites, deuldou):
    for invite in invites:
        ajouterInvite(invite, deuldou)


def inviter(invite, deuldou):
    user = User.objects.get(email=invite.email)
    if user == None:
        # envoi d'une invitation
        print("Envoi d'une invitation à {}".format(invite.email))
    else:
        print("User {} existe, ajout de participation".format(user.email))
        #Participation.objects.create(user=user, deuldou=deuldou)*

"""

""" Fin des Utils de la V1 """

""" Utils de la V2 """

class UserService():
    
    @staticmethod
    def get_Deuldou(rdv_id:int, user: User) -> Deuldou:
        """ Raise une PermissionDenied """
        deuldou: Deuldou = get_object_or_404(Deuldou, pk=rdv_id)
        
        if deuldou.created_by != user :
            raise PermissionDenied
        
        return deuldou
    
    @staticmethod
    def get_Deuldous(user: User) -> list[Deuldou] :
        return Deuldou.objects.filter(created_by=user)
    
    @staticmethod
    def create_Deuldou(user: User, form: Create_Rdv_Form) -> Deuldou :
        return DeuldouService.create_Deuldou_form(user,form)
    
    @staticmethod
    def participate(user: User, rdv:Deuldou) -> None :
        """ Raise ValidationError """
        try:
            ParticipantService.ajouter_Participant(user.email,user.first_name,rdv)
        except ValidationError as error:
            raise error

    @staticmethod
    def add_Participant(user: User, email:str, nom:str, rdv:Deuldou) -> None :
        """ Raise une ValidationError """
        #contact: Contact = ContactService.add_Contact(user,email,nom)
        try:
            ParticipantService.ajouter_Participant(email,nom,rdv)
        except ValidationError as error:
            raise error

    """
    Services Contact
    """
    # Créer un contact
    @staticmethod
    def add_Contact(user: User, email:str, nom:str) -> None :
        """ Raise une ValidationError """
        try:
            ContactService.add_Contact(user, email, nom)
        except ValidationError as error:
            raise error
    
    # Créer une liste de contacts
    @staticmethod
    def create_Liste_contacts(user: User, nom:str) -> Liste_contacts :
        return Liste_contacts.objects.create(user = user, nom=nom)
    
    # Ajouter un contact à une liste
    @staticmethod
    def add_Contact_to_Liste_contacts(user: User, contact: Contact, liste: Liste_contacts) -> bool :
        pass
    """
    Fin des Services Contact
    """

# Services pour le Deuldou
class DeuldouService():
    
    @staticmethod
    def get_Deuldou(rdv_id:int) -> Deuldou:
        return get_object_or_404(Deuldou, pk=rdv_id)
    
    # Créer un Deuldou si le formulaire a été validé
    @staticmethod
    def create_Deuldou_form(user:User, form: Create_Rdv_Form) -> Deuldou:
        nom = form.cleaned_data['nom']
        lieu = form.cleaned_data['lieu']
        jour = form.cleaned_data['jour']
        heure_debut = form.cleaned_data['heure_debut']
        heure_fin = form.cleaned_data['heure_fin']
        createur_participe = form.cleaned_data['createur_participe']
        deuldou: Deuldou = Deuldou.objects.create(created_by=user, nom=nom, lieu=lieu, jour=jour, heure_debut=heure_debut, heure_fin= heure_fin, createur_participe=createur_participe)
        deuldou.save()
        return deuldou
    
    
class ParticipantService():

    """
    @staticmethod
    def __username_exists(email:str) -> bool:
        return User.objects.filter(email=email).exists()
    
    @staticmethod
    def __creer_utilisateur(email:str) -> User:
        # Générer un mdp aléatoire :
        password: str = pwgen(10, symbols=False)
        user:User = User.objects.create_user(
                username=email, email=email, password=password)
        return user
    
    @staticmethod
    def __creer_participant(user: User,nom: str, rdv: Deuldou) -> Participant:
        participant = Participant()
        participant.user = user
        participant.nom = nom
        participant.rdv = rdv
        participant.statut = Participant.VIDE
        try :
            participant.validate_constraints(exclude=None)
        except ValidationError as e :
            print("Participant existe déjà")
            raise Exception("Participant existe déjà")
        else:
            print("Nothing went wrong")
            participant.save()
        return participant
    """
    """
    @staticmethod
    def ajouter_Participant(email: str,nom: str,rdv: Deuldou) -> Participant:
        if not ParticipantService.__username_exists(email):
            user: User = ParticipantService.__creer_utilisateur(email)
        else :
            user:User = User.objects.get(email=email)
        try:
            participant =  ParticipantService.__creer_participant(user,nom,rdv)
            return participant
        except Exception as e:
            raise e
    """

    @staticmethod
    def ajouter_Participant(email: str,nom: str,rdv: Deuldou) -> None:
        """
        Raise une ValidationError\n
        Algo :\n
        Si le mail du Participant n'est pas dans User :
            - Envoyer mail vers formulaire Register (placeholder = email du participant)
        Sinon :
            - Envoyer mail d'info comme nouvelle participation
        """
        try:
            participant: Participant = Participant(email=email, nom=nom, rdv=rdv, statut=Participant.VIDE)
            participant.validate_constraints(exclude=None)
        except ValidationError as error:
            raise error
        else:
            participant.save()
            if User.objects.filter(email=email).exists():
                #send_mail(subject, message, sender, recipients)
                pass
            else :
                #send_mail(subject, message, sender, recipients)
                pass

    """
    @staticmethod
    def add_User(user: User,rdv: Deuldou) -> Participant:
        return ParticipantService.__creer_participant(user, user.first_name, rdv)
    """     


        
        
        

class ContactService():

    @staticmethod
    def add_Contact(user: User, email:str, nom:str) -> Contact :
        """
        Raise une ValidationError
        Ajouter un contact à un User
        un User ne peut pas s'ajouter comme Contact de lui même
        """
        try :
            contact: Contact = Contact(user=user, email=email, nom=nom)
            contact.validate_constraints(exclude=None)
        except ValidationError as error :
            raise error
        else:
            print("Nothing went wrong")
            contact.save()
        return contact

    @staticmethod
    def get_Contacts(user: User):
        return Contact.objects.filter(user=user)