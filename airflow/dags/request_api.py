from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from datetime import datetime

default_args = {
    "owner": "airflow",
    "start_date": datetime(2024, 3, 28),
    "retries": 1,
}

with DAG("dbt_pipeline", default_args=default_args, schedule_interval="*/10 * * * *", catchup=False) as dag:

    request_api = BashOperator(
        task_id="run_request_api",
        bash_command="""
            echo "🔹 Lancement du script de l'API"
            cd /usr/local/airflow/request_api && python3 request.py || echo "❌ Erreur lors de l'exécution du script"
            echo "✅ Exécution du script terminée !"
        """,
        dag=dag
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command="""
            echo "🔹 Lancement de dbt run..."
            cd /usr/local/airflow/dbt && dbt run || echo "❌ Erreur lors de dbt run"
            echo "✅ dbt run terminé !"
        """,
        dag=dag
    )


    request_api >> run_dbt
