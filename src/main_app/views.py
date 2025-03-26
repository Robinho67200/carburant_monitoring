from django.shortcuts import render

# Create your views here.

# views.py


import requests
from geopy.distance import geodesic
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render

from .models import (
    Stations,
    StationWithDiesel,
    StationWithSP95,
    StationWithSP98,
    StationWithE10,
    StationWithE85,
    StationWithGPL,
)


def geocode_address(adresse: str):
    """
    Retourne la latitude et la longitude d'une adresse
    :param adresse:
    :return:
    """
    # Requête pour l'adresse complète
    url_address = f"https://api-adresse.data.gouv.fr/search/?q={adresse}"
    response = requests.get(url_address)

    if response.status_code == 200:
        data = response.json()
        if data["features"]:
            coordinates = data["features"][0]["geometry"]["coordinates"]
            print(f"Coordonnées retournés avec l'adresse")
            print(f"Latitude : {coordinates[1]}")
            print(f"Longitude : {coordinates[0]}")
            return coordinates[1], coordinates[0]  # (lat, lon)

    print(f"probleme à l'adresse {adresse}")
    return None, None  # Si aucune coordonnée n'est trouvée


def get_data(latitude: int, longitude: int, radius_km: int) -> list:
    """
    Retourne la data
    :param latitude:
    :param longitude:
    :param radius_km:
    :return:
    """
    nearby_stores = []

    # Récupérer tous les magasins de la base de données
    all_stations = Stations.objects.all()

    for station in all_stations:
        magasin_coords = (station.latitude, station.longitude)
        user_coords = (latitude, longitude)
        distance = geodesic(user_coords, magasin_coords).kilometers

        if distance <= radius_km:
            distance = round(distance, 2)
            nearby_stores.append(
                {"station": station, "distance": distance}
            )  # Ajouter l'objet magasin et la distance

    # Les 5 stations les moins cher en gazole

    # Extraire les IDs des stations proches
    nearby_station_ids = [entry["station"].id for entry in nearby_stores]

    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_diesel = StationWithDiesel.objects.filter(
        station_id__in=nearby_station_ids
    )
    moyenne_prix_diesel = round(stations_diesel.aggregate(Avg("prix"))["prix__avg"], 2)
    # Trier par prix du Diesel (les 5 moins chères)
    stations_diesel = stations_diesel.order_by("prix")[:5]

    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_sp95 = StationWithSP95.objects.filter(station_id__in=nearby_station_ids)
    moyenne_prix_sp95 = round(stations_sp95.aggregate(Avg("prix"))["prix__avg"], 2)
    # Trier par prix du Diesel (les 5 moins chères)
    stations_sp95 = stations_sp95.order_by("prix")[:5]

    stations_sp98 = StationWithSP98.objects.filter(station_id__in=nearby_station_ids)
    moyenne_prix_sp98 = round(stations_sp98.aggregate(Avg("prix"))["prix__avg"], 2)
    # Trier par prix du Diesel (les 5 moins chères)
    stations_sp98 = stations_sp98.order_by("prix")[:5]

    stations_e10 = StationWithE10.objects.filter(station_id__in=nearby_station_ids)
    moyenne_prix_e10 = round(stations_e10.aggregate(Avg("prix"))["prix__avg"], 2)
    # Trier par prix du Diesel (les 5 moins chères)
    stations_e10 = stations_e10.order_by("prix")[:5]

    stations_e85 = StationWithE85.objects.filter(station_id__in=nearby_station_ids)
    moyenne_prix_e85 = round(stations_e85.aggregate(Avg("prix"))["prix__avg"], 2)
    # Trier par prix du Diesel (les 5 moins chères)
    stations_e85 = stations_e85.order_by("prix")[:5]

    stations_gpl = StationWithGPL.objects.filter(station_id__in=nearby_station_ids)
    moyenne_prix_gpl = round(stations_gpl.aggregate(Avg("prix"))["prix__avg"], 2)
    # Trier par prix du Diesel (les 5 moins chères)
    stations_gpl = stations_gpl.order_by("prix")[:5]

    # Les 10 stations les plus proches
    nearby_stores = sorted(nearby_stores, key=lambda x: x["distance"])[:10]

    return (
        nearby_stores,
        stations_diesel,
        stations_sp95,
        stations_sp98,
        stations_e10,
        stations_e85,
        stations_gpl,
        moyenne_prix_diesel,
        moyenne_prix_sp95,
        moyenne_prix_sp98,
        moyenne_prix_e10,
        moyenne_prix_e85,
        moyenne_prix_gpl,
    )


def fetch_nearby_stations(request, adresse):
    """
    Retourne les stations dans un rayon de 20 km autour d'une adresse
    :param request:
    :param adresse:
    :return:
    """
    # Obtenez les coordonnées de l'adresse
    latitude, longitude = geocode_address(adresse)

    if latitude is None or longitude is None:
        return JsonResponse({"success": False, "error": "Adresse non trouvée."})

    # Récupérer les magasins à proximité
    nearby_stores = get_data(latitude, longitude, 20)

    return nearby_stores


def index(request):
    """
    Vue de la page d'accueil
    :param request:
    :return:
    """
    # Récupérer tous les magasins de la base de données
    all_stations = Stations.objects.all()

    # Ajouter le total du panier au contexte
    context = {"stations": all_stations}

    return render(request, "index.html", context)


def recherche(request):
    """
    Vue de la page recherche
    :param request:
    :return:
    """
    adresse = request.GET.get("adresse", "")

    (
        nearby,
        top5_diesel,
        top5_sp95,
        top5_sp98,
        top5_e10,
        top5_e85,
        top5_gpl,
        moyenne_prix_diesel,
        moyenne_prix_sp95,
        moyenne_prix_sp98,
        moyenne_prix_e10,
        moyenne_prix_e85,
        moyenne_prix_gpl,
    ) = fetch_nearby_stations(request, adresse)

    return render(
        request,
        "recherche.html",
        {
            "adresse": adresse,
            "resultats": nearby,
            "top5_diesel": top5_diesel,
            "top5_sp95": top5_sp95,
            "top5_sp98": top5_sp98,
            "top5_e10": top5_e10,
            "top5_e85": top5_e85,
            "top5_gpl": top5_gpl,
            "moyenne_prix_diesel": moyenne_prix_diesel,
            "moyenne_prix_sp95": moyenne_prix_sp95,
            "moyenne_prix_sp98": moyenne_prix_sp98,
            "moyenne_prix_e10": moyenne_prix_e10,
            "moyenne_prix_e85": moyenne_prix_e85,
            "moyenne_prix_gpl": moyenne_prix_gpl,
        },
    )
