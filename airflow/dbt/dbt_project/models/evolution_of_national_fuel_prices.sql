-- Récupérer la table carburant et faire une moyenne des prix par station, type de carburant et par jour (pour les cas où nous avons plusieurs prix pour une même journée.
-- Ensuite faire une moyenne par journée et par type de carburant

WITH average_price_station_carburant_date AS
(
SELECT station_id_id, DATE(dat_maj) AS date_maj, type_carburant, AVG(prix) as prix
FROM main_app_carburants
GROUP BY station_id_id, date_maj, type_carburant
)

SELECT date_maj, type_carburant, AVG(prix) AS prix_moyen
FROM average_price_station_carburant_date
GROUP BY date_maj, type_carburant
ORDER BY type_carburant, date_maj