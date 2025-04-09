WITH ranking_by_station_carburant AS (
    SELECT
        station_id_id,
        type_carburant,
        prix,
        dat_maj,
        ROW_NUMBER() OVER (PARTITION BY station_id_id, type_carburant ORDER BY dat_maj DESC) AS rn
    FROM main_app_carburants
    WHERE prix != 'nan'
),

last_information AS
(
SELECT
    station_id_id as station_id,
    type_carburant,
    prix,
    dat_maj
FROM ranking_by_station_carburant
WHERE rn = 1
),

classement AS
(
SELECT id,
adresse,
code_postal,
ville,
type_carburant,
prix,
marque,
DENSE_RANK() OVER(PARTITION BY type_carburant ORDER BY prix) as classement
FROM main_app_stations s
LEFT JOIN last_information c ON c.station_id = s.id
)

SELECT *
FROM classement
WHERE classement = 1 AND NOT type_carburant IS NULL