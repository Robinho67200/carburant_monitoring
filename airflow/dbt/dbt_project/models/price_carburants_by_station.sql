SELECT
    station_id_id as station_id,
    c.type_carburant,
    CASE
        WHEN c.prix IS NULL OR c.prix = 'NaN' THEN 0
        ELSE c.prix
    END AS prix
FROM main_app_stations s
LEFT JOIN main_app_carburants c ON c.station_id_id = s.id