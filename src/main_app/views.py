# Create your views here.

# views.py

import requests
from geopy.distance import geodesic
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render
import pandas as pd
import json
from django.views.decorators.cache import cache_page

from .models import (
    Stations,
    StationWithDiesel,
    StationWithSP95,
    StationWithSP98,
    StationWithE10,
    StationWithE85,
    StationWithGPL, Services, Carburants, LastReadingStationFuel, PriceCarburantsByStation, RegionCheaperByFuel,
    StationsCheaperByFuel, EvolutionOfNationalFuelPrices, EvolutionOfStationFuelPrices, AvgPricesByFuel
)

def generation_graphique(carburants_graph):
    try :
        df = pd.DataFrame(list(carburants_graph))

        # Convertir la date
        df["date_maj"] = pd.to_datetime(df["date_maj"]).dt.strftime("%Y-%m-%d")

        # Pivot pour obtenir un tableau date x carburant
        df = df.pivot_table(index="date_maj", columns="type_carburant", values="prix_moyen")

        # S'assurer que toutes les dates sont là
        labels = df.index.tolist()

        color_map = {
            "Diesel": "#D0BC13",
            "SP95": "#95D600",
            "SP98": "#3F6843",
            "E10": "#3F6843",
            "E85": "#109589",
            "GPL": "#34495e",
        }

        datasets = []

        for carburant in df.columns:
            prix = df[carburant].tolist()  # Va contenir des None si valeur manquante

            datasets.append({
                "label": carburant,
                "data": prix,
                "borderColor": color_map.get(carburant, "rgba(0,0,0,1)"),
                "backgroundColor": color_map.get(carburant, "rgba(0,0,0,0.2)"),
                "fill": False,
            })

        graph_data = {
            "labels": labels,
            "datasets": datasets,
        }

    except Exception as e:
        print(e)
        graph_data = 0

    return graph_data

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
    if stations_diesel :
        moyenne_prix_diesel = round(stations_diesel.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        stations_diesel = stations_diesel.order_by("prix")[:5]
    else :
        moyenne_prix_diesel = 0
        stations_diesel = 0

    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_sp95 = StationWithSP95.objects.filter(station_id__in=nearby_station_ids)
    if stations_sp95 :
        moyenne_prix_sp95 = round(stations_sp95.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        stations_sp95 = stations_sp95.order_by("prix")[:5]
    else :
        moyenne_prix_sp95 = 0
        stations_sp95 = 0

    stations_sp98 = StationWithSP98.objects.filter(station_id__in=nearby_station_ids)
    if stations_sp98 :
        moyenne_prix_sp98 = round(stations_sp98.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        stations_sp98 = stations_sp98.order_by("prix")[:5]
    else :
        moyenne_prix_sp98 = 0
        stations_sp98 = 0


    stations_e10 = StationWithE10.objects.filter(station_id__in=nearby_station_ids)
    if stations_e10 :
        moyenne_prix_e10 = round(stations_e10.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        stations_e10 = stations_e10.order_by("prix")[:5]
    else :
        moyenne_prix_e10 = 0
        stations_e10 = 0

    stations_e85 = StationWithE85.objects.filter(station_id__in=nearby_station_ids)
    if stations_e85 :
        moyenne_prix_e85 = round(stations_e85.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        stations_e85 = stations_e85.order_by("prix")[:5]
    else :
        moyenne_prix_e85 = 0
        stations_e85 = 0

    stations_gpl = StationWithGPL.objects.filter(station_id__in=nearby_station_ids)
    if stations_gpl :
        moyenne_prix_gpl = round(stations_gpl.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        stations_gpl = stations_gpl.order_by("prix")[:5]
    else :
        moyenne_prix_gpl = 0
        stations_gpl = 0



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


def fetch_nearby_stations(request, adresse, nb_km_max):
    """
    Retourne les stations dans un rayon de 20 km autour d'une adresse
    :param request:
    :param adresse:
    :param nb_km_max:
    :return:
    """
    # Obtenez les coordonnées de l'adresse
    latitude, longitude = geocode_address(adresse)

    if latitude is None or longitude is None:
        return JsonResponse({"success": False, "error": "Adresse non trouvée."})

    # Récupérer les magasins à proximité
    nearby_stores = get_data(latitude, longitude, nb_km_max)

    return nearby_stores

@cache_page(60 * 60)
def index(request):
    """
    Vue de la page d'accueil
    :param request:
    :return:
    """
    # Récupérer toutes les valeurs sous forme de dictionnaire
    avg_prices = {item.type_carburant: float(item.avg_price) for item in AvgPricesByFuel.objects.all()}

    # Exemple d’accès
    moyenne_prix_diesel = avg_prices.get("Diesel")
    moyenne_prix_e10 = avg_prices.get("E10")
    moyenne_prix_e85 = avg_prices.get("E85")
    moyenne_prix_sp95 = avg_prices.get("SP95")
    moyenne_prix_sp98 = avg_prices.get("SP98")
    moyenne_prix_gpl = avg_prices.get("GPL")

    classement_diesel = RegionCheaperByFuel.objects.filter(type_carburant="Diesel")
    classement_sp95 = RegionCheaperByFuel.objects.filter(type_carburant="SP95")
    classement_sp98 = RegionCheaperByFuel.objects.filter(type_carburant="SP98")
    classement_e10 = RegionCheaperByFuel.objects.filter(type_carburant="E10")
    classement_e85 = RegionCheaperByFuel.objects.filter(type_carburant="E85")
    classement_gpl = RegionCheaperByFuel.objects.filter(type_carburant="GPL")

    stations_cheaper = StationsCheaperByFuel.objects.all()

    # Création du graphique
    carburants_graph = EvolutionOfNationalFuelPrices.objects.all().values("date_maj", "type_carburant", "prix_moyen")
    graph_data = generation_graphique(carburants_graph)

    context = {"moyenne_prix_diesel": moyenne_prix_diesel,
               "moyenne_prix_sp95": moyenne_prix_sp95,
               "moyenne_prix_sp98": moyenne_prix_sp98,
               "moyenne_prix_e10": moyenne_prix_e10,
               "moyenne_prix_e85": moyenne_prix_e85,
               "moyenne_prix_gpl": moyenne_prix_gpl,
               "classement_diesel": classement_diesel,
               "classement_sp95": classement_sp95,
               "classement_sp98": classement_sp98,
               "classement_e10": classement_e10,
               "classement_e85": classement_e85,
               "classement_gpl": classement_gpl,
               "stations_cheaper": stations_cheaper,
               "graph_data": json.dumps(graph_data),
               }

    return render(request, "index.html", context)


def recherche(request):
    """
    Vue de la page recherche
    :param request:
    :return:
    """
    adresse = request.GET.get("adresse", "")
    nb_km_max = request.GET.get("nb_km_max", "")

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
    ) = fetch_nearby_stations(request, adresse, int(nb_km_max))

    # Récupérer la liste des ids de station
    station_ids = [result['station'].id for result in nearby]

    prix_carburants_station = PriceCarburantsByStation.objects.filter(
        station_id__in=station_ids
    )

    # Génération du graphique
    carburants_graph = EvolutionOfStationFuelPrices.objects.filter(
        station_id__in=station_ids
    ).values(
        "date_maj", "type_carburant", "prix_moyen"
    )

    graph_data = generation_graphique(carburants_graph)

    return render(
        request,
        "recherche.html",
        {
            "adresse": adresse,
            "nb_km_max": nb_km_max,
            "resultats": nearby,
            "prix_carburants_station": prix_carburants_station,
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
            "graph_data": json.dumps(graph_data)
        },
    )


@cache_page(60 * 60)
def station(request, id) :
    # Récupérer tous les magasins de la base de données
    station = Stations.objects.filter(id=id).first()
    services = Services.objects.filter(
        station_id=station.id
    ).first()

    carburants = LastReadingStationFuel.objects.filter(
        station_id=station.id
    )

    # Création du graphique
    carburants_graph = EvolutionOfStationFuelPrices.objects.filter(
            station_id=station.id
        ).values(
            "date_maj", "type_carburant", "prix_moyen"
        )

    graph_data = generation_graphique(carburants_graph)

    # Ajouter le total du panier au contexte
    context = {"station": station, 'services' : services.service, "carburants": carburants, "graph_data": json.dumps(graph_data)}

    return render(request, "station.html", context)



@cache_page(60 * 60)
def region(request, id) :

    # Récupérer tous les magasins de la base de données
    all_stations = Stations.objects.filter(nom_region=id)

    # # Récupérer la liste des ids de station
    station_ids = [result.id for result in all_stations]

    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_diesel = StationWithDiesel.objects.filter(
        station_id__in=station_ids
    )
    if stations_diesel :
        moyenne_prix_diesel = round(stations_diesel.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        top5_diesel = stations_diesel.order_by("prix")[:5]
    else :
        moyenne_prix_diesel = 0
        top5_diesel = 0

    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_sp95 = StationWithSP95.objects.filter(station_id__in=station_ids)
    if stations_sp95 :
        moyenne_prix_sp95 = round(stations_sp95.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        top5_sp95 = stations_sp95.order_by("prix")[:5]
    else :
        moyenne_prix_sp95 = 0
        top5_sp95 = 0

    stations_sp98 = StationWithSP98.objects.filter(station_id__in=station_ids)
    if stations_sp98 :
        moyenne_prix_sp98 = round(stations_sp98.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        top5_sp98 = stations_sp98.order_by("prix")[:5]
    else :
        moyenne_prix_sp98 = 0
        top5_sp98 = 0


    stations_e10 = StationWithE10.objects.filter(station_id__in=station_ids)
    if stations_e10 :
        moyenne_prix_e10 = round(stations_e10.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        top5_e10 = stations_e10.order_by("prix")[:5]
    else :
        moyenne_prix_e10 = 0
        top5_e10 = 0

    stations_e85 = StationWithE85.objects.filter(station_id__in=station_ids)
    if stations_e85 :
        moyenne_prix_e85 = round(stations_e85.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        top5_e85 = stations_e85.order_by("prix")[:5]
    else :
        moyenne_prix_e85 = 0
        top5_e85 = 0

    stations_gpl = StationWithGPL.objects.filter(station_id__in=station_ids)
    if stations_gpl :
        moyenne_prix_gpl = round(stations_gpl.aggregate(Avg("prix"))["prix__avg"], 2)
        # Trier par prix du Diesel (les 5 moins chères)
        top5_gpl = stations_gpl.order_by("prix")[:5]
    else :
        moyenne_prix_gpl = 0
        top5_gpl = 0


    # Génération du graphique
    carburants_graph = EvolutionOfStationFuelPrices.objects.filter(
        station_id__in=station_ids
    ).values(
        "date_maj", "type_carburant", "prix_moyen"
    )

    graph_data = generation_graphique(carburants_graph)

    context = {"stations": all_stations,
               "region": id,
               "moyenne_prix_diesel": moyenne_prix_diesel,
               "moyenne_prix_sp95": moyenne_prix_sp95,
               "moyenne_prix_sp98": moyenne_prix_sp98,
               "moyenne_prix_e10": moyenne_prix_e10,
               "moyenne_prix_e85": moyenne_prix_e85,
               "moyenne_prix_gpl": moyenne_prix_gpl,
               "graph_data": json.dumps(graph_data),
               "top5_diesel": top5_diesel,
               "top5_sp95": top5_sp95,
               "top5_sp98": top5_sp98,
               "top5_e10": top5_e10,
               "top5_e85": top5_e85,
               "top5_gpl": top5_gpl,
               }

    return render(request, "region.html", context)

@cache_page(60 * 60)
def departement(request, id) :

    # Récupérer tous les magasins de la base de données
    all_stations = Stations.objects.filter(nom_departement=id)

    region = all_stations.first().nom_region

    # # Récupérer la liste des ids de station
    station_ids = [result.id for result in all_stations]


    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_diesel = StationWithDiesel.objects.filter(station_id__in=station_ids)
    moyenne_prix_diesel = round(stations_diesel.aggregate(Avg("prix"))["prix__avg"], 2)

    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_sp95 = StationWithSP95.objects.filter(station_id__in=station_ids)
    moyenne_prix_sp95 = round(stations_sp95.aggregate(Avg("prix"))["prix__avg"], 2)

    stations_sp98 = StationWithSP98.objects.filter(station_id__in=station_ids)
    moyenne_prix_sp98 = round(stations_sp98.aggregate(Avg("prix"))["prix__avg"], 2)

    stations_e10 = StationWithE10.objects.filter(station_id__in=station_ids)
    moyenne_prix_e10 = round(stations_e10.aggregate(Avg("prix"))["prix__avg"], 2)

    stations_e85 = StationWithE85.objects.filter(station_id__in=station_ids)
    moyenne_prix_e85 = round(stations_e85.aggregate(Avg("prix"))["prix__avg"], 2)

    stations_gpl = StationWithGPL.objects.filter(station_id__in=station_ids)
    moyenne_prix_gpl = round(stations_gpl.aggregate(Avg("prix"))["prix__avg"], 2)

    top5_diesel = stations_diesel.order_by('prix')[:5]
    top5_sp95 = stations_sp95.order_by('prix')[:5]
    top5_sp98 = stations_sp98.order_by('prix')[:5]
    top5_e10 = stations_e10.order_by('prix')[:5]
    top5_e85 = stations_e85.order_by('prix')[:5]
    top5_gpl = stations_gpl.order_by('prix')[:5]


    # Génération du graphique
    carburants_graph = EvolutionOfStationFuelPrices.objects.filter(
        station_id__in=station_ids
    ).values(
        "date_maj", "type_carburant", "prix_moyen"
    )

    graph_data = generation_graphique(carburants_graph)

    context = {"stations": all_stations,
               'region': region,
               "departement": id,
               "moyenne_prix_diesel": moyenne_prix_diesel,
               "moyenne_prix_sp95": moyenne_prix_sp95,
               "moyenne_prix_sp98": moyenne_prix_sp98,
               "moyenne_prix_e10": moyenne_prix_e10,
               "moyenne_prix_e85": moyenne_prix_e85,
               "moyenne_prix_gpl": moyenne_prix_gpl,
               "graph_data": json.dumps(graph_data),
               "top5_diesel": top5_diesel,
               "top5_sp95": top5_sp95,
               "top5_sp98": top5_sp98,
               "top5_e10": top5_e10,
               "top5_e85": top5_e85,
               "top5_gpl": top5_gpl,
               }

    return render(request, "departement.html", context)


@cache_page(60 * 60)
def ville(request, id) :

    # Récupérer tous les magasins de la base de données
    all_stations = Stations.objects.filter(ville=id)

    region = all_stations.first().nom_region
    departement = all_stations.first().nom_departement


    # # Récupérer la liste des ids de station
    station_ids = [result.id for result in all_stations]

    print(station_ids)

    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_diesel = StationWithDiesel.objects.filter(station_id__in=station_ids)
    if stations_diesel :
        moyenne_prix_diesel = round(stations_diesel.aggregate(Avg("prix"))["prix__avg"], 2)
    else :
        moyenne_prix_diesel = 0

    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_sp95 = StationWithSP95.objects.filter(station_id__in=station_ids)
    if stations_sp95 :
        moyenne_prix_sp95 = round(stations_sp95.aggregate(Avg("prix"))["prix__avg"], 2)
    else:
        moyenne_prix_sp95 = 0

    stations_sp98 = StationWithSP98.objects.filter(station_id__in=station_ids)
    if stations_sp98 :
        moyenne_prix_sp98 = round(stations_sp98.aggregate(Avg("prix"))["prix__avg"], 2)
    else :
        moyenne_prix_sp98 = 0

    stations_e10 = StationWithE10.objects.filter(station_id__in=station_ids)
    if stations_e10:
        moyenne_prix_e10 = round(stations_e10.aggregate(Avg("prix"))["prix__avg"], 2)
    else:
        moyenne_prix_e10 = 0

    stations_e85 = StationWithE85.objects.filter(station_id__in=station_ids)
    if stations_e85 :
        moyenne_prix_e85 = round(stations_e85.aggregate(Avg("prix"))["prix__avg"], 2)
    else:
        moyenne_prix_e85 = 0

    stations_gpl = StationWithGPL.objects.filter(station_id__in=station_ids)
    if stations_gpl :
        moyenne_prix_gpl = round(stations_gpl.aggregate(Avg("prix"))["prix__avg"], 2)
    else :
        moyenne_prix_gpl = 0

    top5_diesel = stations_diesel.order_by('prix')[:5]
    if len(top5_diesel) == 0 :
        top5_diesel = 0
    top5_sp95 = stations_sp95.order_by('prix')[:5]
    if len(top5_sp95) == 0 :
        top5_sp95 = 0
    top5_sp98 = stations_sp98.order_by('prix')[:5]
    if len(top5_sp98) == 0 :
        top5_sp98 = 0
    top5_e10 = stations_e10.order_by('prix')[:5]
    if len(top5_e10) == 0 :
        top5_e10 = 0
    top5_e85 = stations_e85.order_by('prix')[:5]
    if len(top5_e85) == 0 :
        top5_e85 = 0
    top5_gpl = stations_gpl.order_by('prix')[:5]
    if len(top5_gpl) == 0 :
        top5_gpl = 0


    prix_carburants_station = PriceCarburantsByStation.objects.filter(
        station_id__in=station_ids
    )

    # Génération du graphique
    carburants_graph = EvolutionOfStationFuelPrices.objects.filter(
        station_id__in=station_ids
    ).values(
        "date_maj", "type_carburant", "prix_moyen"
    )

    graph_data = generation_graphique(carburants_graph)

    context = {"stations": all_stations,
               "ville": id,
               "region": region,
               "departement": departement,
               "prix_carburants_station": prix_carburants_station,
               "moyenne_prix_diesel": moyenne_prix_diesel,
               "moyenne_prix_sp95": moyenne_prix_sp95,
               "moyenne_prix_sp98": moyenne_prix_sp98,
               "moyenne_prix_e10": moyenne_prix_e10,
               "moyenne_prix_e85": moyenne_prix_e85,
               "moyenne_prix_gpl": moyenne_prix_gpl,
               "graph_data": json.dumps(graph_data),
               "top5_diesel": top5_diesel,
               "top5_sp95": top5_sp95,
               "top5_sp98": top5_sp98,
               "top5_e10": top5_e10,
               "top5_e85": top5_e85,
               "top5_gpl": top5_gpl,
               }

    return render(request, "ville.html", context)