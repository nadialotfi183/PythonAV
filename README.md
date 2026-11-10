# Pipeline d’Analyse de Logs SSH
Ce projet consiste à créer un programme Python qui analyse les logs SSH pour détecter les tentatives de connexion, localiser les adresses IP et afficher les résultats sous forme de statistiques et de graphiques.

# Exécution
Installation des dépendances :
uv sync
Lancement du projet :
python main.py

Le chargement de la base IPinfo prend environ une minute. Il faut fermer la fenêtre du graphique pour terminer le programme.

Le pipeline suit 5 étapes : ingestion, parsing, géolocalisation, agrégation et dashboard.

# Résultats du dashboard
Le programme affiche les échecs par pays, les connexions réussies par utilisateur et les tentatives avec un utilisateur invalide.

Lors du dernier test, il a détecté 958 tentatives invalides, géolocalisé 692 IP et identifié 69 pays. Les Pays-Bas (NL) étaient en tête des échecs. Les résultats sont affichés dans le terminal et enregistrés dans `output/dashboard.png`.

# Choix techniques
J'utilise une base IPinfo locale pour éviter les appels Internet et un cache pour ne pas rechercher plusieurs fois la même IP. Les tentatives `invalid user` sont prises en compte dans les échecs par pays sans compter deux fois la même tentative.

# Logging et gestion d'erreurs
Les logs sont enregistrés dans `logs/app.log`, avec plusieurs niveaux de suivi et une rotation à 1 Mo avec 3 sauvegardes. Chaque module gère les erreurs liées à son fonctionnement, comme la lecture, le traitement et la géolocalisation des fichiers.

# Limites
Aucune connexion réussie n'est présente dans les logs, donc le graphique correspondant affiche un message. Les pays sont affichés avec leurs codes (NL, CN...) et les lignes qui ne concernent pas les connexions SSH réussies ou échouées sont ignorées.

# Organisation Git
J'ai travaillé progressivement, avec un commit et un push après chaque module terminé.


# Structure du projet
- `ingestion/` : lecture des fichiers logs.
- `processing/` : analyse, géolocalisation et agrégation.
- `dashboard/` : affichage des résultats et création des graphiques.
- `data/` : contient les 4 fichiers `auth.log` et le dossier `geo/`.
- `data/geo/` : contient la base IPinfo.
- `logger.py` : gestion des logs et des erreurs.
- `main.py` : lancement du pipeline.
- `logs/` : stockage de `app.log`.
- `output/` : stockage de `dashboard.png`.

Les dossiers `logs/` et `output/` sont créés automatiquement.

# Prérequis
Le projet utilise Python, uv et matplotlib. Les modules `re`, `gzip`, `csv`, `ipaddress`, `bisect`, `logging`, `os` et `collections` sont inclus dans Python.

La base gratuite `ipinfo_lite.csv.gz` est à télécharger sur [ipinfo.io](https://ipinfo.io/) et à placer dans `data/geo/`. Elle doit être téléchargée séparément si elle n'est pas présente sur GitHub.