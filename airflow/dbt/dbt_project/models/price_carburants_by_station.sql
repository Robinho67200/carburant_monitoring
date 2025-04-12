WITH carburants_disponibles AS (
    -- Liste des types de carburants disponibles
    SELECT 'Diesel' AS type_carburant
    UNION
    SELECT 'Essence'
    UNION
    SELECT 'GPL'
    UNION
    SELECT 'SP95'
    UNION
    SELECT 'SP98'
    UNION
    SELECT 'E10'
    UNION
    SELECT 'E85'
),

ranking_by_station_carburant AS (
    SELECT
        station_id_id,
        type_carburant,
        prix,
        dat_maj,
        ROW_NUMBER() OVER (PARTITION BY station_id_id, type_carburant ORDER BY dat_maj DESC) AS rn
    FROM main_app_carburants
),

last_station_carburant AS (
SELECT *
FROM ranking_by_station_carburant
WHERE rn = 1
),

stations_carburants_complets AS (
    -- Créer toutes les combinaisons possibles de station_id et type_carburant
    SELECT s.id AS station_id, c.type_carburant
    FROM main_app_stations s
    CROSS JOIN carburants_disponibles c
)

SELECT
    s.station_id,
    s.type_carburant,
    COALESCE(c.prix, 0) AS prix
FROM stations_carburants_complets s
LEFT JOIN last_station_carburant c
    ON s.station_id = c.station_id_id
    AND s.type_carburant = c.type_carburant
ORDER BY s.station_id, s.type_carburant