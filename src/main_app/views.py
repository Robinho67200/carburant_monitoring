from django.shortcuts import render

# Create your views here.

# views.py


import requests
from geopy.distance import geodesic
from django.db.models import Avg
from django.http import JsonResponse
from django.shortcuts import render
import plotly.io as pio

from .models import (
    Stations,
    StationWithDiesel,
    StationWithSP95,
    StationWithSP98,
    StationWithE10,
    StationWithE85,
    StationWithGPL, Services, Carburants, LastReadingStationFuel, PriceCarburantsByStation, RegionCheaperByFuel,
    StationsCheaperByFuel, EvolutionOfNationalFuelPrices, EvolutionOfStationFuelPrices,
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


import plotly.express as px
import pandas as pd

def index(request):
    """
    Vue de la page d'accueil
    :param request:
    :return:
    """
    # Récupérer tous les magasins de la base de données
    all_stations = Stations.objects.all()


    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_diesel = StationWithDiesel.objects.all()
    moyenne_prix_diesel = round(stations_diesel.aggregate(Avg("prix"))["prix__avg"], 2)

    # Filtrer les stations Diesel en ne gardant que celles présentes dans nearby_stores
    stations_sp95 = StationWithSP95.objects.all()
    moyenne_prix_sp95 = round(stations_sp95.aggregate(Avg("prix"))["prix__avg"], 2)

    stations_sp98 = StationWithSP98.objects.all()
    moyenne_prix_sp98 = round(stations_sp98.aggregate(Avg("prix"))["prix__avg"], 2)

    stations_e10 = StationWithE10.objects.all()
    moyenne_prix_e10 = round(stations_e10.aggregate(Avg("prix"))["prix__avg"], 2)

    stations_e85 = StationWithE85.objects.all()
    moyenne_prix_e85 = round(stations_e85.aggregate(Avg("prix"))["prix__avg"], 2)

    stations_gpl = StationWithGPL.objects.all()
    moyenne_prix_gpl = round(stations_gpl.aggregate(Avg("prix"))["prix__avg"], 2)


    classement_diesel = RegionCheaperByFuel.objects.filter(type_carburant="Diesel")
    classement_sp95 = RegionCheaperByFuel.objects.filter(type_carburant="SP95")
    classement_sp98 = RegionCheaperByFuel.objects.filter(type_carburant="SP98")
    classement_e10 = RegionCheaperByFuel.objects.filter(type_carburant="E10")
    classement_e85 = RegionCheaperByFuel.objects.filter(type_carburant="E85")
    classement_gpl = RegionCheaperByFuel.objects.filter(type_carburant="GPL")

    stations_cheaper = StationsCheaperByFuel.objects.all()

    # Génération du graphique
    carburants_graph = EvolutionOfNationalFuelPrices.objects.all().values(
        "date_maj", "type_carburant", "prix_moyen"
    )
    df = pd.DataFrame(list(carburants_graph))
    df["date_maj"] = pd.to_datetime(df["date_maj"])

    fig = px.line(
        df,
        x="date_maj",
        y="prix_moyen",
        color="type_carburant",
        markers=True,
        labels={"date_maj": "Date", "prix_moyen": "Prix moyen (€)", "type_carburant": "Carburant"},
    )

    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Prix moyen (€)",
        xaxis=dict(tickformat="%Y-%m-%d"),
        hovermode="x unified",
        paper_bgcolor="white",
        plot_bgcolor="white",
    )

    graph_html = pio.to_html(fig, full_html=False)

    context = {"stations": all_stations,
               "moyenne_prix_diesel": moyenne_prix_diesel,
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
               "graph_html": graph_html
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
        },
    )



def station(request, id) :
    # Récupérer tous les magasins de la base de données
    station = Stations.objects.filter(id=id).first()
    services = Services.objects.filter(
        station_id=station.id
    ).first()

    carburants = LastReadingStationFuel.objects.filter(
        station_id=station.id
    )

    try :
        # Génération du graphique
        carburants_graph = EvolutionOfStationFuelPrices.objects.filter(
            station_id=station.id
        ).values(
            "date_maj", "type_carburant", "prix_moyen"
        )
        df = pd.DataFrame(list(carburants_graph))
        df["date_maj"] = pd.to_datetime(df["date_maj"])

        fig = px.line(
            df,
            x="date_maj",
            y="prix_moyen",
            color="type_carburant",
            markers=True,
            labels={"date_maj": "Date", "prix_moyen": "Prix moyen (€)", "type_carburant": "Carburant"},
        )

        fig.update_layout(
            xaxis_title="Date",
            yaxis_title="Prix moyen (€)",
            xaxis=dict(tickformat="%Y-%m-%d"),
            hovermode="x unified",
            paper_bgcolor="white",
            plot_bgcolor="white",
        )

        graph_html = pio.to_html(fig, full_html=False)

    except :
        graph_html = 0

    # Ajouter le total du panier au contexte
    context = {"station": station, 'services' : services.service, "carburants": carburants, "graph_html": graph_html}

    return render(request, "station.html", context)