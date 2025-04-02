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
last_information AS (
SELECT
    station_id_id as station_id,
    type_carburant,
    prix,
    dat_maj
FROM ranking_by_station_carburant
WHERE rn = 1
),

region_carburant AS
(
SELECT nom_region,
       type_carburant,
       ROUND(CAST(AVG(prix) AS NUMERIC), 3) AS prix_moyen
FROM main_app_stations s
LEFT JOIN last_information c ON c.station_id = s.id
WHERE prix != 'nan' AND NOT nom_region IS NULL
GROUP BY nom_region, type_carburant
)


SELECT
CONCAT(nom_region, '_', type_carburant) AS id,
*,
DENSE_RANK() OVER(PARTITION BY type_carburant ORDER BY prix_moyen) AS classement
FROM region_carburant


