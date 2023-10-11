from django import forms
from django.core.exceptions import ValidationError

from .models import Contact, Deuldou, Liste_contacts, Participant

"""
class Create_Rdv_Form(forms.Form):
    nom = forms.CharField(label='rendez-vous', max_length=100)
    jour = forms.DateField(label="date")
    heure_debut = forms.TimeField(label="début")
    heure_fin = forms.TimeField(label="fin", required=False)
    lieu = forms.CharField(label="lieu", widget=forms.Textarea, max_length=100)
    createur_participe = forms.BooleanField(label='Vous participez ?', initial=True, required=False)

    def clean(self):
        cleaned_data = super().clean()
        fin = cleaned_data.get("heure_fin")
        debut = cleaned_data.get("heure_debut")

        if fin is None :
            cleaned_data["heure_fin"] = '00:00'

        if debut is None :
            cleaned_data["heure_debut"] = '00:00'
"""

# Rdv Form V2
class RdvForm(forms.ModelForm):
    class Meta:
        model = Deuldou
        fields = ['nom','jour','heure_debut','heure_fin','lieu']

    # Clean pour test du template errors
    def clean_nom(self):
        data = self.cleaned_data["nom"]
        if "Q1" in data:
            raise ValidationError("Q1 is not allowed !")
        return data
    
    def clean_lieu(self):
        data = self.cleaned_data["lieu"]
        if "Q1" in data:
            raise ValidationError("Q1 is not allowed in lieu !")

        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return data
    
    def clean(self):
        cleaned_data = super().clean()
        fin = cleaned_data.get("heure_fin")
        debut = cleaned_data.get("heure_debut")

        if fin is None :
            cleaned_data["heure_fin"] = '00:00'

        if debut is None :
            cleaned_data["heure_debut"] = '00:00'
    
    

class Add_Participant_Form(forms.Form):
    email = forms.EmailField(max_length=100)
    nom = forms.CharField(max_length=100)
    statut= forms.CharField(max_length=2,widget=forms.Select(choices=Participant.STATUTS_CHOICES))

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["rdv", "email", "nom"]
        widgets = {'rdv': forms.HiddenInput()}
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        rdv = self.cleaned_data["rdv"]
        if Participant.objects.filter(email=email, rdv=rdv).exists():
            raise ValidationError("{} est déjà enregistré pour ce Rendez-vous".format(email))
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return email

class HTMXParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["nom","statut"]
        #widgets = {'rdv': forms.HiddenInput()}

"""
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"
        widgets = {'user': forms.HiddenInput()}

"""

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        #fields = "__all__"
        exclude = ["user"]
        #widgets = {'user': forms.HiddenInput()}

    # Override de la méthode pour form.is_valid() -> prendre en compte contrainte Unique sur User
    def _get_validation_exclusions(self):
        exclude = super(ContactForm, self)._get_validation_exclusions()
        exclude.remove('user')
        return exclude




class Liste_contactsForm(forms.ModelForm):
    class Meta:
        model = Liste_contacts
        exclude = ["contacts"]
        widgets = {'user': forms.HiddenInput()}