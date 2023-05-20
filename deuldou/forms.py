from django import forms

from .models import Contact, Liste_contacts, Participant


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


class Add_Participant_Form(forms.Form):
    email = forms.EmailField(max_length=100)
    nom = forms.CharField(max_length=100)
    statut= forms.CharField(max_length=2,widget=forms.Select(choices=Participant.STATUTS_CHOICES))

class ParticipantForm(forms.ModelForm):
    class Meta:
        model = Participant
        fields = ["rdv", "email", "nom"]
        widgets = {'rdv': forms.HiddenInput()}

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

class Liste_contactsForm(forms.ModelForm):
    class Meta:
        model = Liste_contacts
        exclude = ["contacts"]
        widgets = {'user': forms.HiddenInput()}