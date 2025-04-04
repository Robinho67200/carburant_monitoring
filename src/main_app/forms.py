from django import forms

class AdresseForm(forms.ModelForm):
    adresse = forms.CharField(label="Adresse", max_length=450)
    nb_km_max = forms.FloatField(
        label="Distance maximale en km", min_value=5, max_value=40, initial=10
    )

    class Meta:
        fields = ["adresse", "nb_km_max"]