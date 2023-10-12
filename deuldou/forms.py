from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from .models import Contact, Deuldou, Liste_contacts, Participant


# Rdv Form V2
class RdvForm(forms.ModelForm):
    class Meta:
        model = Deuldou
        fields = ['nom','jour','heure_debut','heure_fin','lieu']

    def clean(self):
        cleaned_data = super().clean()
        fin = cleaned_data.get("heure_fin")
        debut = cleaned_data.get("heure_debut")

        if fin is None :
            cleaned_data["heure_fin"] = '00:00'

        if debut is None :
            cleaned_data["heure_debut"] = '00:00'
    
    
"""
class Add_Participant_Form(forms.Form):
    email = forms.EmailField(max_length=100)
    nom = forms.CharField(max_length=100)
    statut= forms.CharField(max_length=2,widget=forms.Select(choices=Participant.STATUTS_CHOICES))
"""


class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["rdv", "email", "nom"]
        widgets = {'rdv': forms.HiddenInput()}

        error_messages = {
            "email": {
                "required": _("L'émail est obligatoire"),
            },
            "nom": {
                "required": _("Un nom est obligatoire"),
            },
        }
    
    def clean_email(self):
        email = self.cleaned_data["email"]
        rdv = self.cleaned_data["rdv"]
        if Participant.objects.filter(email=email, rdv=rdv).exists():
            raise ValidationError("{} est déjà enregistré pour ce Rendez-vous".format(email))
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return email


# Formulaire à renommer -> ParticipantUpdate
class HTMXParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["nom","statut"]
        #widgets = {'rdv': forms.HiddenInput()}


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"
        widgets = {'user': forms.HiddenInput()}

    def clean_email(self):
        email = self.cleaned_data["email"]
        user = self.cleaned_data["user"]
        if Contact.objects.filter(email=email, user=user).exists():
            raise ValidationError("{} est déjà enregistré pour ce Rendez-vous".format(email))
        # Always return a value to use as the new cleaned data, even if
        # this method didn't change it.
        return email


class Liste_contactsForm(forms.ModelForm):
    class Meta:
        model = Liste_contacts
        exclude = ["contacts"]
        widgets = {'user': forms.HiddenInput()}