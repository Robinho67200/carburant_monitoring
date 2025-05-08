# Projet Monitoring du prix du carburant en France

## Présentation vidéo du projet

[![Watch the video](https://img.youtube.com/vi/8e9nn5UQJIk/maxresdefault.jpg)](https://youtu.be/8e9nn5UQJIk)

### [Regarder cette vidéo sur YouTube](https://youtu.be/8e9nn5UQJIk)


## Présentation du projet
J’ai développé mon-carburant.fr qui combine data engineering et analyse intelligente des données pour répondre à une question simple mais importante :
Où faire le plein au meilleur prix ?

Grâce à une collecte automatisée de données sur les stations-service en France, je peux vous proposer :

-  Des statistiques détaillées sur l’évolution des prix du carburant
-  Des comparaisons par région, par type de carburant, ou encore par période
-  Une recherche personnalisée selon votre localisation ou vos trajets

## Fonctionnement :

### Fonctionnement de l'application

1. **Saisie de l'adresse et du rayon de recherche**  
L’utilisateur saisit son adresse et définit un rayon de recherche pour localiser les stations-service dans la zone de son choix.

2. **Affichage des résultats détaillés**  
Une fois la recherche effectuée, l’utilisateur accède à une page présentant plusieurs éléments :
   - **Statistiques détaillées** sur les prix du carburant dans la zone choisie
   - **Courbe d'évolution des prix** pour suivre les tendances dans le secteur
   - **Stations les moins chères** classées par type de carburant
   - **Liste des stations les plus proches**, avec les prix et distances correspondants

3. **Statistiques spécifiques pour une station sélectionnée**  
L’utilisateur peut également consulter des **statistiques détaillées** et une **courbe d'évolution des prix** pour la station-service qu’il sélectionne, afin d’avoir une vue complète de son historique tarifaire.

---

### Fonctionnalités supplémentaires

- **Statistiques au niveau national** : Sur la page d'accueil, l’utilisateur peut visualiser des statistiques globales sur l’évolution des prix du carburant à l’échelle nationale, accompagnées d'une courbe d’évolution.
  
- **Exploration régionale, départementale et locale** : L’utilisateur peut affiner sa recherche en accédant à des pages spécifiques aux régions, départements, et villes. Chaque niveau offre des **statistiques détaillées** et des **courbes d’évolution des prix**, permettant ainsi une exploration approfondie des données à différentes échelles géographiques.



## URL du projet
https://mon-carburant.fr/

## Stack technique
- Django : Framework web Python pour développer des applications robustes et sécurisées.
- PostgreSQL : Base de données relationnelle performante et fiable.
- Docker : Conteneurisation pour un déploiement stable et reproductible.
- Nginx : Serveur web et proxy inverse optimisant performances et sécurité.
- Git : Gestion de versions et automatisation CI/CD via GitHub Actions.
- Airflow : Outil d’ingénierie des données pour pipelines ETL.
- DBT : Outil de transformation des données permettant de gérer les modèles, automatiser les tests et garantir la qualité des données au sein des pipelines ETL.

## Architecture

![Image](https://github.com/user-attachments/assets/0701136f-11ad-4319-ae25-e6d77a7ee47b)

## Prochaines étapes
- **Améliorer la détection des enseignes**  
  Certaines stations ne sont pas correctement identifiées : affiner les requêtes API pour une détection plus fiable des enseignes.

- **Ajouter de nouvelles statistiques** :
  - Évolution des prix sur différentes périodes : **30 jours**, **6 mois** et **1 an**.
  - **Comparaison par enseigne** pour identifier les marques les plus économiques.

- **Intégrer les prix des bornes de recharge électrique**  
  Étendre l’application aux véhicules électriques en ajoutant les tarifs des bornes.

- **Enrichir les données des stations**  
  Ajouter les **horaires d’ouverture** et les informations de **rupture de stock** (carburants indisponibles) pour une vision plus complète.
