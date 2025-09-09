WITH latest_diesel AS (
    SELECT
        type_carburant,
        prix,
        ROW_NUMBER() OVER (PARTITION BY station_id_id, type_carburant ORDER BY dat_maj DESC) AS rn
    FROM main_app_carburants
)

SELECT type_carburant, ROUND(AVG(prix)::numeric(10,2), 2) AS avg_price
FROM latest_diesel
WHERE rn = 1
GROUP BY type_carburant
