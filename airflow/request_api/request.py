from io import BytesIO
import json
import requests
import pandas as pd
from glom import glom
import psycopg2
from psycopg2 import Error
import os
from dotenv import load_dotenv
from datetime import datetime
import pytz
import overpy

load_dotenv()

# Lire une variable d'environnement
DB_NAME = os.getenv("DB_NAME_CARBURANTS")
USER = os.getenv("USER_CARBURANTS")
PASSWORD = os.getenv("PASSWORD_CARBURANTS")
HOST = os.getenv("HOST_CARBURANTS")
PORT = os.getenv("PORT_CARBURANTS")




def extraire_horaires(dictionnaire:str|dict) -> dict:
    """
    Fonction pour extraire les horaires

    :param dictionnaire: données brutes contenant les horaires
    :return: (dict) : les horaires par jour.
    """
    try:
        dictionnaire = json.loads(dictionnaire)

        # Extraire les jours à l'aide de glom
        horaires_jours = glom(dictionnaire, "jour", default=[])

        result = {}

        for jour in horaires_jours:
            nom_jour = jour["@nom"]

            # Vérifier la structure de 'horaire' (soit une liste, soit un dictionnaire unique)
            horaires = jour.get("horaire", None)

            if isinstance(horaires, list):
                # Si c'est une liste, traiter comme avant
                horaires_list = [
                    {"ouverture": h["@ouverture"], "fermeture": h["@fermeture"]}
                    for h in horaires
                ]
            elif isinstance(horaires, dict):
                # Si c'est un dictionnaire unique, traiter en conséquence
                horaires_list = [
                    {
                        "ouverture": horaires["@ouverture"],
                        "fermeture": horaires["@fermeture"],
                    }
                ]
            else:
                # Si 'horaire' est absent ou a une structure inattendue
                horaires_list = []

            # Ajouter à notre dictionnaire
            result[nom_jour] = horaires_list

    except TypeError:
        result = None

    return result


def get_fuel_stations(lat, lon, radius=500):
    query = f"""
    node(around:{radius},{lat},{lon})["amenity"="fuel"];
    out;
    """

    result = api.query(query)

    stations = []
    for node in result.nodes:
        if node.tags.get("name", "Inconnu") == "Inconnu" and node.tags.get("operator", "Inconnu") != "Inconnu":
            stations.append({
                "id": row['id'],
                "name": node.tags.get("operator", "Inconnu"),
                "marque": node.tags.get("operator", "Inconnu")
            })
        else :
            stations.append({
                "id": row['id'],
                "name": node.tags.get("name", "Inconnu"),
                "marque": node.tags.get("operator", "Inconnu")
            })

    return stations


def assign_marque(row):
    for marque_normalisee, noms_possibles in marques_mapping.items():
        for nom in noms_possibles:
            if nom == row:
                if marque_normalisee == 'Autre':
                    return nom
                return marque_normalisee

    return None


def normaliser_texte(texte):
    if not isinstance(texte, str):
        return ''
    return texte.lower()

def transform_brand(x):
    texte = normaliser_texte(x)
    for marque, mots_cles in mot_clefs_par_marque.items():
        if any(mot in texte for mot in mots_cles):
            return marque
    return 'Indépendant'

connection = psycopg2.connect(
    dbname=DB_NAME,
    user=USER,
    password=PASSWORD,
    host=HOST,
    port=PORT,
)

cursor = connection.cursor()
connection.commit()

r = requests.get(
    "https://data.economie.gouv.fr/api/explore/v2.1/catalog/datasets/prix-des-carburants-en-france-flux-instantane-v2/exports/parquet"
)
df = pd.read_parquet(BytesIO(r.content), engine="pyarrow")


# Création de la table station
stations = (
    df[
        [
            "id",
            "latitude",
            "longitude",
            "cp",
            "adresse",
            "ville",
            "departement",
            "code_departement",
            "region",
            "code_region",
            "horaires_automate_24_24",
        ]
    ]
    .copy()
    .drop_duplicates()
)
stations.rename(
    columns={
        "cp": "code_postal",
        "departement": "nom_departement",
        "region": "nom_region",
        "horaires_automate_24_24": "automate_24_24",
    },
    inplace=True,
)
stations["automate_24_24"] = stations["automate_24_24"].apply(
    lambda x: True if x == "Oui" else False
)
stations["latitude"] = stations["latitude"].astype(float)
stations["latitude"] = stations["latitude"].apply(lambda x : x/100000)
stations["longitude"] = stations["longitude"].astype(float)
stations["longitude"] = stations["longitude"].apply(lambda x : x/100000)
stations["automate_24_24"] = stations["automate_24_24"].astype(bool)


cursor.execute("SELECT id FROM main_app_stations")

colonnes = [desc[0] for desc in cursor.description]

donnees = cursor.fetchall()

df_stations = pd.DataFrame(donnees, columns=colonnes)

stations["id"] = stations["id"].astype(str)
df_stations["id"] = df_stations["id"].astype(str)

stations = stations[~stations["id"].isin(df_stations["id"])]

api = overpy.Overpass()

first_stations = []
for _, row in stations.iterrows():
    stations_nearby = get_fuel_stations(row['latitude'], row['longitude'])

    if stations_nearby:
        first_station = stations_nearby[0]
    else:
        first_station = {
            "id": row['id'],
            "name": "Inconnu",
            "marque": "Inconnu"
        }

    first_stations.append(first_station)

stations_with_names = pd.DataFrame(first_stations)

if len(stations) != 0 :
    stations =(
        stations
        .merge(stations_with_names, how="inner", on="id")
    )

# Dictionnaire : marque normalisée -> valeurs possibles dans la colonne "marque"
marques_mapping = {
    'Total': [
        'Total', 'TOTAL', 'total',
        "Relais Total du Bol d'or", 'Relais Total des Aubrais',
        'Relais Total de la Porte Océane', 'Relais Total de Pomméniac',
        'Relais Total du Bocage', "Relais Total de L'espace Saint-Germain"
    ],
    'Total Energies': [
        'TotalEnergies', 'Total Energies', 'Total Energy',
        'TotalEnergies Access', 'Totalenergies', 'TotalEnergie', 'Total Energie'
    ],
    'Total Access': ['Total Access', 'Total Acces', 'total access'],
    'Intermarché': [
        'Intermarché', 'Groupement des Mousquetaires', 'intermarché',
        'Intermarché contact', 'Intermarché Barjols', 'Les Mousquetaires',
        'Groupement Les Mousquetaires', 'Groupement les mousquetaires'
    ],
    'Carrefour Contact': ['carrefour contact', 'Carrefour Contact'],
    'Carrefour Market': ['Carrefour Market', 'Carrefour market - Trilport'],
    'Carrefour': ['Carrefour', 'Groupe Carrefour'],
    'Esso': ['Esso', 'Esso S.A.F.', 'esso'],
    'Système U': [
        'Super U', 'U Express', 'U express', 'Super U La Tranche Sur Mer',
        'Système U', 'Hyper U', 'Magasins U'
    ],
    'Avia': ['Avia', 'AVIA', 'avia'],
    'Auchan': ['Auchan', 'Auchan Carburants', 'Groupe Auchan', 'Auchan Saint-Genis-Laval'],
    'Shell': ['Shell', 'SHELL', 'shell'],
    'Leclerc': ['E. Leclerc', 'E.Leclerc', 'Leclerc', 'E. Leclerc Ville-la-Grand'],
    'Casino': ['Casino', 'Groupe Casino', 'Casino Carburants'],
    'Elan': ['Elan', 'ELAN'],
    'Eni': ['Eni', 'ENI France SARL', 'ENI'],
    'Elf': ['Elf', 'elf'],
    'Netto': ['Netto', 'netto'],
    'Colruyt': ['Colruyt', 'Colruyt Group'],
    'Autre': [
        'Esso Express', 'Carrefour Express', 'BP', 'Cora', 'Agip', 'Vito',
        'Dyneff', 'Fulli', 'Spar', 'Match', 'Leader Price', 'Shopi'
    ]
}

if len(stations) != 0 :
    stations['marque'] = stations['marque'].apply(assign_marque)

    stations_normalisées = stations[stations['marque'].notna()]

    id = stations_normalisées['id'].tolist()
    stations = stations[~stations['id'].isin(id)]
    stations['marque'] = ""

# Dictionnaire des marques : marque normalisée → liste de mots-clés à détecter
mot_clefs_par_marque = {
    'Intermarché': ['intermarché'],
    'Carrefour Contact': ['carrefour contact'],
    'Carrefour Market': ['carrefour market'],
    'Carrefour': ['carrefour'],
    'Système U': ['station u', 'système u', 'super u', 'u express', 'hyper u', 'marché u'],
    'Avia': ['avia'],
    'Total Access': ['total access'],
    'Esso Express': ['esso express'],
    'Total Energies': ['totalenergies', 'total energies'],
    'Auchan': ['auchan', 'atac'],
    'Casino': ['casino'],
    'Dyneff': ['dyneff'],
    'Netto': ['netto'],
    'Match': ['match'],
    'Shell': ['shell'],
    'Spar': ['spar'],
    'Colruyt': ['dats 24'],
    'Elan': ['elan'],
    'G20': ['g20'],
    'Vito': ['vito'],
    'Total': ['total'],
    'Leclerc': ['leclerc'],
    'Esso': ['esso'],
    'BP': ['bp'],
    'Eni': ['eni'],
    'Agip': ['agip'],
    'Utile': ['utile'],
    'Maximarché': ['maximarché'],
    'Bi1': ['bi1'],
}

if len(stations) != 0 :
    stations['marque'] = stations['name'].apply(transform_brand)

    stations = pd.concat([
        stations_normalisées,
        stations
    ], ignore_index=True)


# Création de la table services
services = df[["id", "services_service"]].copy()
services.rename(columns={"id": "station_id"}, inplace=True)
services["service"] = services["services_service"].apply(
    lambda x: x.split(",") if isinstance(x, str) else []
)

# Création de la table horaires
horaires = df[["id", "horaires"]].copy()
horaires.rename(columns={"id": "station_id"}, inplace=True)
horaires["horaires"] = horaires["horaires"].apply(extraire_horaires)

# Création de la table ruptures
ruptures = df[["id", "rupture"]].copy()
ruptures.rename(columns={"id": "station_id"}, inplace=True)

# Création de la table carburants
carburants_gazole = df[["id", "gazole_maj", "gazole_prix"]].copy()
carburants_gazole.rename(
    columns={"id": "station_id", "gazole_maj": "dat_maj", "gazole_prix": "prix"},
    inplace=True,
)
carburants_gazole["type_carburant"] = "Diesel"

carburants_sp95 = df[["id", "sp95_maj", "sp95_prix"]].copy()
carburants_sp95.rename(
    columns={"id": "station_id", "sp95_maj": "dat_maj", "sp95_prix": "prix"},
    inplace=True,
)
carburants_sp95["type_carburant"] = "SP95"

carburants_e85 = df[["id", "e85_maj", "e85_prix"]].copy()
carburants_e85.rename(
    columns={"id": "station_id", "e85_maj": "dat_maj", "e85_prix": "prix"}, inplace=True
)
carburants_e85["type_carburant"] = "E85"

carburants_gpl = df[["id", "gplc_maj", "gplc_prix"]].copy()
carburants_gpl.rename(
    columns={"id": "station_id", "gplc_maj": "dat_maj", "gplc_prix": "prix"},
    inplace=True,
)
carburants_gpl["type_carburant"] = "GPL"


carburants_e10 = df[["id", "e10_maj", "e10_prix"]].copy()
carburants_e10.rename(
    columns={"id": "station_id", "e10_maj": "dat_maj", "e10_prix": "prix"}, inplace=True
)
carburants_e10["type_carburant"] = "E10"

carburants_sp98 = df[["id", "sp98_maj", "sp98_prix"]].copy()
carburants_sp98.rename(
    columns={"id": "station_id", "sp98_maj": "dat_maj", "sp98_prix": "prix"},
    inplace=True,
)
carburants_sp98["type_carburant"] = "SP98"


carburants = pd.concat(
    [
        carburants_gazole,
        carburants_sp95,
        carburants_e85,
        carburants_gpl,
        carburants_e10,
        carburants_sp98,
    ],
    axis=0,
)
carburants["dat_maj"] = carburants["dat_maj"].replace({pd.NaT: None})

carburants = carburants.dropna(subset=["dat_maj"])
today = datetime.now(pytz.timezone("Europe/Paris"))
carburants["date_diff"] = carburants["dat_maj"].apply(lambda x : (today-x).days )
carburants = carburants.query("date_diff <=4")


carburants = carburants.sort_values('dat_maj', ascending=False)

cursor.execute("SELECT * FROM main_app_carburants")

colonnes = [desc[0] for desc in cursor.description]

donnees = cursor.fetchall()

df_carburants = pd.DataFrame(donnees, columns=colonnes)

df_carburants.rename(columns={'station_id_id': 'station_id'}, inplace=True)

carburants["station_id"] = carburants["station_id"].astype(str)
df_carburants["station_id"] = df_carburants["station_id"].astype(str)

carburants["dat_maj"] = carburants["dat_maj"].astype(str)
df_carburants["dat_maj"] = df_carburants["dat_maj"].astype(str)

colonnes = ["station_id", "type_carburant", "prix", "dat_maj"]

df_unique = carburants.merge(df_carburants, on=colonnes, how="left", indicator=True)
carburants = df_unique[df_unique["_merge"] == "left_only"].drop(columns="_merge")


for index, row in stations.iterrows():
    cursor.execute(
        """
        INSERT INTO main_app_stations (
            id,
            latitude,
            longitude,
            code_postal,
            adresse,
            ville,
            nom_departement,
            code_departement,
            nom_region,
            code_region,
            automate_24_24,
            marque
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT ("id") DO NOTHING
    """,
        (
            row["id"],
            row["latitude"],
            row["longitude"],
            row["code_postal"],
            row["adresse"],
            row["ville"],
            row["nom_departement"],
            row["code_departement"],
            row["nom_region"],
            row["code_region"],
            row["automate_24_24"],
            row["marque"]
        ),
    )

connection.commit()

for index, row in services.iterrows():
    cursor.execute(
        """
        INSERT INTO main_app_services (
            station_id_id,
            service
        )
        VALUES (%s, %s)
        ON CONFLICT ("station_id_id") DO UPDATE
        SET service = EXCLUDED.service;
    """,
        (row["station_id"], json.dumps(row["service"])),
    )

connection.commit()

for index, row in horaires.iterrows():
    cursor.execute(
        """
        INSERT INTO main_app_horaires (
            station_id_id,
            horaires
        )
        VALUES (%s, %s)
        ON CONFLICT ("station_id_id") DO UPDATE
        SET horaires = EXCLUDED.horaires;
    """,
        (row["station_id"], json.dumps(row["horaires"])),
    )

connection.commit()

for index, row in carburants.iterrows():
    try :
        cursor.execute(
            """
            INSERT INTO main_app_carburants (
                station_id_id,
                type_carburant,
                prix,
                dat_maj
            )
            VALUES (%s, %s, %s, %s)
        """,
            (
                row["station_id"],
                row["type_carburant"],
                row["prix"],
                row["dat_maj"],
            ),
        )
    except Error as e:
        print(f"⚠️ Insertion ignorée (doublon ?) : {e}")

connection.commit()

cursor.close()
connection.close()

print("Données insérées avec succès!")
