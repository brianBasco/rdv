
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models
from django.utils import timezone


# Create your models here.
class Utilisateur(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    modifier_password = models.BooleanField(default=True)

class Tag(models.Model):
    """
    Une étiquette permet de marquer l'invitation à l'aide d'un mot-clé
    afin de regrouper les invitations par mot-clé (pour l'affichage)
    """
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='etiquettes')
    nom = models.CharField(max_length=100)
    is_checked = models.BooleanField(default=True)

    def __str__(self):
        return self.nom

class Deuldou(models.Model):
    # attributs
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deuldous_crees")
    created_at = models.DateTimeField(default=timezone.now)
    nom = models.CharField(max_length=100, null=False)
    jour = models.DateField(null=False)
    heure_debut = models.TimeField(default='00:00')
    heure_fin = models.TimeField(default='00:00')
    lieu = models.TextField(null=False, max_length=100)
    # config :
    # nombre min = minimum de participants à participer pour valider le rdv
    nbre_min = models.IntegerField(default=0)
    createur_participe = models.BooleanField(default=False)

    def __str__(self):
        return self.nom

# Un user peut créer des étiquettes pour les affecter à ses deuldous :
# exemple : étiquette match ou entrainement ou travail etc...
# Un User ne peut pas s'inscrire 2 fois à un deuldou :
# Contrainte unique sur les clés deuldou et user

"""
class Meta:
    constraints = [
        models.UniqueConstraint(
            fields=["deuldou", "user"], name='participation unique'),
    ]
"""


class Statut(models.Model):
    nom = models.CharField(max_length=50)



# -----------------------Modèle V1 -----------------------------------------------
class Invite(models.Model):
    """
    Un invité s'inscrit à un Rdv avec son email (ces 2 champs sont obligatoires)
    Si l'invité s'inscrit alors il devra choisir son statut
    """
    """ ------------ Obligatoire-------- """
    deuldou = models.ForeignKey(
        Deuldou, on_delete=models.CASCADE, related_name='invites')
    email = models.CharField(max_length=200)
    """ ------------ Facultatif-------- """
    est_inscrit = models.BooleanField(default=False)
    statut = models.ForeignKey(Statut, on_delete=models.DO_NOTHING, null=True)
    visible = models.BooleanField(default=True)
    invited_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invites', null=True)
    prenom = models.CharField(max_length=100, null=True, blank=True)
    nom = models.CharField(max_length=100, null=True, blank=True)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    commentaire = models.TextField(null=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.email

    """
    Un Invité ne peut pas être invité 2 fois à un même deuldou :
    un Invité est identifié grâce à son email
    Contrainte unique sur les clés deuldou et email    
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["deuldou", "email"], name='invitation unique'),
        ]





class Liste_invitation(models.Model):
    """ Un User peut enregistrer ses invitations dans des listes : """
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='listes_invitation')
    nom = models.CharField(max_length=100)
    invites = models.ManyToManyField(Invite)

    def __str__(self):
        return self.nom

# --------------------------- Fin du Modèle V1 -------------------------------------------



# --------------------------- Modèle V2 -------------------------------------------


""" class Participant(models.Model):
    \""" ------------ Choix -------- \"""
    PRESENT = "PR"
    ABSENT = "AB"
    RETARD = "RE"
    INCERTAIN = "IN"
    VIDE = "VI"
    STATUTS_CHOICES = [
        (PRESENT, "Présent"),
        (ABSENT, "Absent"),
        (RETARD, "En retard"),
        (INCERTAIN, "Incertain"),
        (VIDE, "Non inscrit"),
    ]
    \""" ------------ Obligatoire-------- \"""
    rdv = models.ForeignKey(
        Deuldou, on_delete=models.CASCADE, related_name='participants')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='participations')
    nom = models.CharField(max_length=200, default="anonyme")
    \""" ------------ Facultatif-------- \"""
    statut = models.CharField(max_length=2,choices=STATUTS_CHOICES,default=VIDE)
    visible = models.BooleanField(default=True)
    commentaire = models.TextField(null=True)
    tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.nom

    \"""
    Contrainte unique sur les clés RDV et USER    
    \"""
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rdv", "user"], name='participation unique'),
        ] """



class Participant(models.Model):
    """ ------------ Choix -------- """
    PRESENT = "PR"
    ABSENT = "AB"
    RETARD = "RE"
    INCERTAIN = "IN"
    VIDE = "VI"
    STATUTS_CHOICES = [
        (PRESENT, "Présent"),
        (ABSENT, "Absent"),
        (RETARD, "En retard"),
        (INCERTAIN, "Incertain"),
    ]
    """ ------------ Obligatoire-------- """
    rdv = models.ForeignKey(Deuldou, on_delete=models.CASCADE, related_name='participants')
    email = models.EmailField(max_length=100, blank=False)
    nom = models.CharField(max_length=150, blank=False)
    """ ------------ Facultatif-------- """
    statut = models.CharField(max_length=2,choices=STATUTS_CHOICES,default=(VIDE, "Non inscrit"))
    visible = models.BooleanField(default=True)
    commentaire = models.TextField(null=True, blank=True)
    #tags = models.ManyToManyField(Tag)

    def __str__(self):
        return self.nom

    """
    Contrainte unique sur les clés RDV et EMAIL    
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["rdv", "email"], name='participation unique', violation_error_message="Ce participant existe déjà"),
        ]



""" ----------------  CONTACTS ----------------------- """


class Contact(models.Model):
    """
    Contraintes :
    - Un contact appartient à UN User et un user peut avoir des contacts et des listes de contacts
    - Un User ne peut pas avoir 2 contacts avec la même adresse email
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='contacts')
    email = models.EmailField(max_length=150, blank=False)
    nom = models.CharField(max_length=150, blank=False)

    def __str__(self):
        return self.nom
    
    def clean(self) -> None:
        """
        Un User ne peut pas être Contact de lui même :
        """
        if self.user.email == self.email :
            #raise ValidationError("Vous ne pouvez pas vous ajouter")
            raise ValidationError({"email": "Vous ne pouvez pas ajouter comme Contact"})
        
        
    """
    Contrainte unique sur les clés USER et EMAIL    
    """
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "email"], name='contact unique', violation_error_message="Ce contact existe déjà")
        ]


class Liste_contacts(models.Model):
    """
    Un User peut enregistrer plusieurs listes \n
    Un contact peut appartenir à plusieurs listes (exemple, contact(seb) appartient à entrainement et matchs)\n
    contraintes:\n
    - unique pour : USER et NOM
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liste_contacts')
    nom = models.CharField(max_length=100)
    contacts = models.ManyToManyField(Contact)

    class Meta:
        ordering = ['nom']
        constraints = [
            models.UniqueConstraint(
                fields=["user", "nom"], name='liste unique', violation_error_message="Cette liste existe déjà")
        ]

    def __str__(self):
        return self.nom
    
    
""" ----------------  FIN DES CONTACTS ----------------------- """