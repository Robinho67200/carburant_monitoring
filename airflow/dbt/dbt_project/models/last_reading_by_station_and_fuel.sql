WITH ranking_by_station_carburant AS (
    SELECT
        station_id_id,
        type_carburant,
        prix,
        dat_maj,
        ROW_NUMBER() OVER (PARTITION BY station_id_id, type_carburant ORDER BY dat_maj DESC) AS rn
    FROM main_app_carburants
    WHERE prix != 'nan'
)

SELECT
    station_id_id as station_id,
    type_carburant,
    prix,
    dat_maj
FROM ranking_by_station_carburant
WHERE rn = 1
