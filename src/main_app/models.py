from django.db import models

# Create your models here.


class stations(models.Model):
    id = models.CharField(primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    code_postal = models.CharField(null=True)
    adresse = models.CharField(null=True)
    ville = models.CharField(null=True)
    nom_departement = models.CharField(null=True)
    code_departement = models.CharField(null=True)
    nom_region = models.CharField(null=True)
    code_region = models.CharField(null=True)
    automate_24_24 = models.BooleanField()


class carburants(models.Model):
    station_id = models.ForeignKey(stations, on_delete=models.CASCADE) # mettre nom station_id car la colonne se nomme station_id_id
    type_carburant = models.CharField()
    prix = models.FloatField(null=True)
    dat_maj = models.DateTimeField(null=True)

    class Meta:
        unique_together = ('station_id', 'type_carburant', 'prix', 'dat_maj')

class ruptures(models.Model):
    station_id = models.OneToOneField(stations, on_delete=models.CASCADE)
    type_carburant = models.CharField()
    rupture_debut = models.DateField()
    type_rupture = models.CharField()

class services(models.Model):
    station_id = models.OneToOneField(stations, on_delete=models.CASCADE)
    service = models.JSONField(null=True)  # Modifier en liste

class horaires(models.Model):
    station_id = models.OneToOneField(stations, on_delete=models.CASCADE)
    horaires = models.JSONField()
