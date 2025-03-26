from django import forms


class AdresseForm(forms.ModelForm):
    adresse = forms.CharField(label="Adresse", max_length=450)
