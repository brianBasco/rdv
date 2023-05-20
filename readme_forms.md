https://docs.djangoproject.com/en/4.2/ref/forms/validation/
Exemple de validation, a lieu lors de l'appel à form.is_valid() :
Ceci permet de nettoyer un formulaire. Si l'on veut nettoyer un champ en général (Field), il faut mieux utiliser Validate()

class ContactForm(forms.Form):
    # Everything as before.
    ...

    def clean(self):
        cleaned_data = super().clean()
        cc_myself = cleaned_data.get("cc_myself")
        subject = cleaned_data.get("subject")

        if cc_myself and subject and "help" not in subject:
            msg = "Must put 'help' in subject when cc'ing yourself."
            self.add_error("cc_myself", msg)
            self.add_error("subject", msg)