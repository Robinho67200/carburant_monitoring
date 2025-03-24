from django.db import models

# Create your models here.


class stations(models.Model):
    id = models.CharField(primary_key=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    code_postal = models.CharField()
    adresse = models.CharField()
    ville = models.CharField()
    nom_departement = models.CharField()
    code_departement = models.CharField()
    nom_region = models.CharField()
    code_region = models.CharField()


class carburants(models.Model):
    id = models.CharField(primary_key=True)
    station_id = models.ForeignKey(stations, on_delete=models.CASCADE)
    type_carburant = models.CharField()
    prix = models.FloatField()
    dat_maj = models.DateField()


class ruptures(models.Model):
    id = models.CharField(primary_key=True)
    station_id = models.ForeignKey(stations, on_delete=models.CASCADE)
    type_carburant = models.CharField()
    rupture_debut = models.DateField()
    type_rupture = models.CharField()

class services(models.Model):
    id = models.CharField(primary_key=True)
    station_id = models.ForeignKey(stations, on_delete=models.CASCADE)
    service = models.CharField()

class horraires(models.Model):
    id = models.CharField(primary_key=True)
    station_id = models.ForeignKey(stations, on_delete=models.CASCADE)
    jour = models.CharField()
    horraires = models.CharField()
    automate_24_24 = models.BooleanField()
