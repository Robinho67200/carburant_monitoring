from django.db import models

# Create your models here.


class Stations(models.Model):
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


class Carburants(models.Model):
    station_id = models.ForeignKey(
        Stations, on_delete=models.CASCADE
    )  # mettre nom station_id car la colonne se nomme station_id_id
    type_carburant = models.CharField()
    prix = models.FloatField(null=True)
    dat_maj = models.DateTimeField(null=True)

    class Meta:
        unique_together = ("station_id", "type_carburant", "prix", "dat_maj")


class Ruptures(models.Model):
    station_id = models.OneToOneField(Stations, on_delete=models.CASCADE)
    type_carburant = models.CharField()
    rupture_debut = models.DateField()
    type_rupture = models.CharField()


class Services(models.Model):
    station_id = models.OneToOneField(Stations, on_delete=models.CASCADE)
    service = models.JSONField(null=True)  # Modifier en liste


class Horaires(models.Model):
    station_id = models.OneToOneField(Stations, on_delete=models.CASCADE)
    horaires = models.JSONField()


class StationWithDiesel(models.Model):
    station_id = models.CharField(primary_key=True)
    adresse = models.CharField(max_length=255, null=True)
    ville = models.CharField(max_length=255, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    code_postal = models.CharField(max_length=10, null=True)
    automate_24_24 = models.BooleanField()
    prix = models.FloatField(null=True)
    dat_maj = models.DateTimeField(null=True)
    days_difference = models.IntegerField()

    class Meta:
        managed = False
        db_table = "stations_with_diesel"


class StationWithSP95(models.Model):
    station_id = models.CharField(primary_key=True)
    adresse = models.CharField(max_length=255, null=True)
    ville = models.CharField(max_length=255, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    code_postal = models.CharField(max_length=10, null=True)
    automate_24_24 = models.BooleanField()
    prix = models.FloatField(null=True)
    dat_maj = models.DateTimeField(null=True)
    days_difference = models.IntegerField()

    class Meta:
        managed = False
        db_table = "stations_with_sp95"


class StationWithSP98(models.Model):
    station_id = models.CharField(primary_key=True)
    adresse = models.CharField(max_length=255, null=True)
    ville = models.CharField(max_length=255, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    code_postal = models.CharField(max_length=10, null=True)
    automate_24_24 = models.BooleanField()
    prix = models.FloatField(null=True)
    dat_maj = models.DateTimeField(null=True)
    days_difference = models.IntegerField()

    class Meta:
        managed = False
        db_table = "stations_with_sp98"


class StationWithGPL(models.Model):
    station_id = models.CharField(primary_key=True)
    adresse = models.CharField(max_length=255, null=True)
    ville = models.CharField(max_length=255, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    code_postal = models.CharField(max_length=10, null=True)
    automate_24_24 = models.BooleanField()
    prix = models.FloatField(null=True)
    dat_maj = models.DateTimeField(null=True)
    days_difference = models.IntegerField()

    class Meta:
        managed = False
        db_table = "stations_with_gpl"


class StationWithE10(models.Model):
    station_id = models.CharField(primary_key=True)
    adresse = models.CharField(max_length=255, null=True)
    ville = models.CharField(max_length=255, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    code_postal = models.CharField(max_length=10, null=True)
    automate_24_24 = models.BooleanField()
    prix = models.FloatField(null=True)
    dat_maj = models.DateTimeField(null=True)
    days_difference = models.IntegerField()

    class Meta:
        managed = False
        db_table = "stations_with_e10"


class StationWithE85(models.Model):
    station_id = models.CharField(primary_key=True)
    adresse = models.CharField(max_length=255, null=True)
    ville = models.CharField(max_length=255, null=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    code_postal = models.CharField(max_length=10, null=True)
    automate_24_24 = models.BooleanField()
    prix = models.FloatField(null=True)
    dat_maj = models.DateTimeField(null=True)
    days_difference = models.IntegerField()

    class Meta:
        managed = False
        db_table = "stations_with_e85"


class LastReadingStationFuel(models.Model):
    station_id = models.CharField(primary_key=True)
    type_carburant = models.CharField()
    prix = models.FloatField(null=True)
    dat_maj = models.DateTimeField(null=True)
    days_difference = models.IntegerField()

    class Meta:
        managed = False
        db_table = "last_reading_by_station_and_fuel"

class PriceCarburantsByStation(models.Model):
    station_id = models.CharField(primary_key=True)
    type_carburant = models.CharField()
    prix = models.FloatField(null=True)

    class Meta:
        managed = False
        db_table = "price_carburants_by_station"


class RegionCheaperByFuel(models.Model):
    id = models.CharField(primary_key=True)
    nom_region = models.CharField(null=True)
    type_carburant = models.CharField()
    prix_moyen = models.FloatField(null=True)
    classement = models.IntegerField()

    class Meta:
        managed = False
        db_table = "region_cheaper_by_fuel"


class StationsCheaperByFuel(models.Model):
    id = models.CharField(primary_key=True)
    adresse = models.CharField(null=True)
    code_postal = models.CharField(null=True)
    ville = models.CharField(null=True)
    type_carburant = models.CharField()
    prix = models.FloatField(null=True)
    classement = models.IntegerField()

    class Meta:
        managed = False
        db_table = "stations_cheaper_by_fuel"
