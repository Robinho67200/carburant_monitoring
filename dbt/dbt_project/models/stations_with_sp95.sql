WITH latest_sp95 AS (
    SELECT
        station_id_id,
        prix,
        dat_maj,
        ROW_NUMBER() OVER (PARTITION BY station_id_id ORDER BY dat_maj DESC) AS rn
    FROM main_app_carburants
    WHERE type_carburant = 'SP 95' AND prix != 'nan'
)

SELECT
    s.id AS station_id,
    s.adresse,
    s.ville,
    s.latitude,
    s.longitude,
    s.code_postal,
    s.automate_24_24,
    ld.prix,
    ld.dat_maj
FROM main_app_stations s
LEFT JOIN latest_sp95 ld ON s.id = ld.station_id_id
WHERE ld.rn = 1