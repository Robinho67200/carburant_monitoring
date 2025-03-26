from io import BytesIO
import json
import requests
import pandas as pd
from glom import glom
import psycopg2
from psycopg2 import Error

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
carburants_sp95["type_carburant"] = "SP 95"

carburants_e85 = df[["id", "e85_maj", "e85_prix"]].copy()
carburants_e85.rename(
    columns={"id": "station_id", "e85_maj": "dat_maj", "e85_prix": "prix"}, inplace=True
)
carburants_e85["type_carburant"] = "E 85"

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
carburants_e10["type_carburant"] = "E 10"

carburants_sp98 = df[["id", "sp98_maj", "sp98_prix"]].copy()
carburants_sp98.rename(
    columns={"id": "station_id", "sp98_maj": "dat_maj", "sp98_prix": "prix"},
    inplace=True,
)
carburants_sp98["type_carburant"] = "SP 98"


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


# Connexion à votre base de données PostgreSQL
connection = psycopg2.connect(
    dbname="carburant_monitoring",
    user="robin",
    password="azerty",
    host="172.17.0.2",
    port="5432",
)

cursor = connection.cursor()
connection.commit()

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
            automate_24_24
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
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
    except Error:
        pass

connection.commit()

cursor.close()
connection.close()

print("Données insérées avec succès!")
