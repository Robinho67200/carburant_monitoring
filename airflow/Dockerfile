FROM python:3.10

# Définir les variables d'environnement pour Airflow
ENV AIRFLOW_HOME=/usr/local/airflow
ENV AIRFLOW_VERSION=2.5.3
ENV PYTHONPATH="$PYTHONPATH:/usr/local/airflow/dags"

# Installer git, cron et les dépendances dbt
RUN apt-get update && apt-get install -y git cron && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip && pip install wheel dbt-core dbt-postgres

# Copier la configuration de la base de données
COPY dbt/dbt_project/profiles/profiles.yml $AIRFLOW_HOME/dbt/profiles.yml
# Copier uniquement les fichiers indispensables
COPY dbt/dbt_project/dbt_project.yml $AIRFLOW_HOME/dbt
COPY dbt/dbt_project/models/ $AIRFLOW_HOME/dbt/models/

COPY request_api/request.py $AIRFLOW_HOME/request_api/request.py

COPY request_api/request.py $AIRFLOW_HOME/request_api/request.py

# Mettre à jour les paquets et installer les dépendances nécessaires
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    libssl-dev \
    git \
    && apt-get clean

# Copier le dossier dags dans le conteneur
COPY dags $AIRFLOW_HOME/dags

# Installer Airflow
RUN pip install apache-airflow==${AIRFLOW_VERSION} \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.9.txt"

# Installer les dépendances supplémentaires
RUN pip install pytz
RUN pip install psycopg[binary]==3.1.12 psycopg2-binary==2.9.9 requests pandas glom pyarrow python-dotenv overpy

RUN pip install --upgrade typing_extensions

# Créer un utilisateur Airflow
RUN useradd -ms /bin/bash airflow

# Changer le répertoire de travail
WORKDIR $AIRFLOW_HOME

# Exposer les ports nécessaires
EXPOSE 8080