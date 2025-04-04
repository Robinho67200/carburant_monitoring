SELECT station_id_id AS station_id, DATE(dat_maj) AS date_maj, type_carburant, AVG(prix) as prix_moyen
FROM main_app_carburants
GROUP BY station_id_id, date_maj, type_carburant
ORDER BY station_id_id, type_carburant, date_maj