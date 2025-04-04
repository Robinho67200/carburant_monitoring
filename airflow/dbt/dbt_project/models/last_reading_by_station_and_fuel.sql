--WITH ranking_by_station_carburant AS (
--    SELECT
--        station_id_id,
--        type_carburant,
--        prix,
--        dat_maj,
--        ROW_NUMBER() OVER (PARTITION BY station_id_id, type_carburant ORDER BY dat_maj DESC) AS rn
--    FROM main_app_carburants
--    WHERE prix != 'nan'
--)
--
--SELECT
--    station_id_id as station_id,
--    type_carburant,
--    prix,
--    dat_maj,
--    (CURRENT_DATE - dat_maj::DATE) AS days_difference
--FROM ranking_by_station_carburant
--WHERE rn = 1


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

last_price_by_station_fuel AS (
SELECT
    station_id_id as station_id,
    type_carburant,
    prix,
    dat_maj,
    (CURRENT_DATE - dat_maj::DATE) AS days_difference,
    s.code_departement,
    s.code_region,
    s.ville
FROM ranking_by_station_carburant c
INNER JOIN main_app_stations s ON s.id = c.station_id_id
WHERE rn = 1
),

average_price_by_fuel_and_department AS (
SELECT code_departement, type_carburant, AVG(prix) AS avg_prix_department
FROM last_price_by_station_fuel
GROUP BY code_departement, type_carburant
),

average_price_by_fuel_and_region AS (
SELECT code_region, type_carburant, AVG(prix) AS avg_prix_region
FROM last_price_by_station_fuel
GROUP BY code_region, type_carburant
),

average_price_by_fuel_and_city AS (
SELECT ville, type_carburant, AVG(prix) AS avg_prix_city
FROM last_price_by_station_fuel
GROUP BY ville, type_carburant
)


SELECT
    c.station_id,
    c.type_carburant,
    c.prix,
    c.dat_maj,
    c.days_difference,
    ROUND(((CAST(c.prix AS NUMERIC) - CAST(av.avg_prix_department AS NUMERIC)) / CAST(av.avg_prix_department AS NUMERIC)) * 100, 2) AS pourcentage_variation_department,
    ROUND(((CAST(c.prix AS NUMERIC) - CAST(avre.avg_prix_region AS NUMERIC)) / CAST(avre.avg_prix_region AS NUMERIC)) * 100, 2) AS pourcentage_variation_region,
    ROUND(((CAST(c.prix AS NUMERIC) - CAST(avci.avg_prix_city AS NUMERIC)) / CAST(avci.avg_prix_city AS NUMERIC)) * 100, 2) AS pourcentage_variation_city
FROM last_price_by_station_fuel c
INNER JOIN average_price_by_fuel_and_department av ON av.code_departement = c.code_departement AND av.type_carburant = c.type_carburant
INNER JOIN average_price_by_fuel_and_region avre ON avre.code_region = c.code_region AND avre.type_carburant = c.type_carburant
INNER JOIN average_price_by_fuel_and_city avci ON avci.ville = c.ville AND avci.type_carburant = c.type_carburant
