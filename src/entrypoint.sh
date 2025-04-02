#!/bin/sh

# Vérifier si la base de données est prête (PostgreSQL)
if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $SQL_HOST $SQL_PORT; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

# Effectuer les migrations de la base de données
echo "Applying database migrations..."
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

# Démarrer Gunicorn
echo "Starting Gunicorn..."
#gunicorn carburant_monitoring_web.wsgi:application --bind 0.0.0.0:6000 &
exec gunicorn carburant_monitoring_web.wsgi:application --bind 0.0.0.0:6000