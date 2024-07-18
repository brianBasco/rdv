chatgpt v3.5
Dans Django, vous pouvez étendre le modèle User de base pour permettre à un utilisateur d'avoir plusieurs adresses e-mails. Vous pouvez également ajouter une vérification d'adresse e-mail personnalisée. Voici un exemple de code pour illustrer cela :
N'oubliez pas de créer et appliquer les migrations après avoir ajouté ces modèles. Vous pouvez également personnaliser davantage ce code en fonction de vos besoins spécifiques. Assurez-vous d'avoir également configuré les paramètres de messagerie dans vos paramètres Django pour pouvoir envoyer des e-mails de vérification.

# models.py

from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    email = models.EmailField(unique=True)
    additional_emails = models.ManyToManyField('AdditionalEmail', blank=True)

class AdditionalEmail(models.Model):
    email = models.EmailField(unique=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    verified = models.BooleanField(default=False)

# signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        AdditionalEmail.objects.create(user=instance, email=instance.email, verified=True)
# views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import AddEmailForm
from .models import AdditionalEmail

@login_required
def add_email(request):
    if request.method == 'POST':
        form = AddEmailForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if not AdditionalEmail.objects.filter(email=email).exists():
                additional_email = AdditionalEmail.objects.create(user=request.user, email=email)
                # Envoyer un e-mail de vérification ici si nécessaire
                messages.success(request, 'L\'adresse e-mail a été ajoutée avec succès.')
            else:
                messages.error(request, 'Cette adresse e-mail existe déjà.')
            return redirect('add_email')
    else:
        form = AddEmailForm()

    additional_emails = AdditionalEmail.objects.filter(user=request.user)
    return render(request, 'add_email.html', {'form': form, 'additional_emails': additional_emails})

# forms.py

from django import forms

class AddEmailForm(forms.Form):
    email = forms.EmailField()

# add_email.html

{% extends 'base.html' %}

{% block content %}
  <h2>Ajouter une adresse e-mail</h2>
  <form method="post">
    {% csrf_token %}
    {{ form.as_p }}
    <button type="submit">Ajouter</button>
  </form>

  <h2>Adresses e-mail ajoutées</h2>
  <ul>
    {% for additional_email in additional_emails %}
      <li>{{ additional_email.email }}{% if additional_email.verified %} (vérifiée){% endif %}</li>
    {% endfor %}
  </ul>
{% endblock %}
