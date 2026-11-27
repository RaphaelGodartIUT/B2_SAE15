# SAÉ 15 - Carte des installations radioélectriques (Groupe B2)

Programme Python qui analyse les données de l'ANFR et crée une carte interactive des supports d'antennes en France métropolitaine.

Groupe B2 : Mathias CAPLET, Hévy POULOLO, Djabhar MMADI-ABDOU, Raphaël GODART, Antoine VERDURE

## Structure du projet

Le dossier SAE15 contient :

- **carte_antennes.py** : le programme principal ;
- **le dossier data**, avec les données de l'ANFR : sup_support.txt, sup_station.txt, sup_antenne.txt et sup_emetteur.txt ;
- **le dossier ref**, avec les tables de référence : sup_exploitant.txt et sup_nature.txt ;
- **carte_antennes.html** : la carte créée quand on lance le programme ;
- **graphiques.png** : les graphiques créés par le programme, affichés dans le cadre de la carte.

## Structure du code

**TÊTE : la préparation**

- Modules : os, webbrowser, pandas, folium, matplotlib, folium.plugins : MarkerCluster
- Constantes : GENERATIONS (système vers 2G/3G/4G/5G), OPERATEURS, fond de carte IGN

**CORPS : les fonctions, en 4 parties**

- Charger les données
  - lecture() : lit un fichier ANFR
  - nombresss() : transforme du texte en nombres
  - donnees_chargement() : charge, nettoie et relie les tables
- Préparer les infos
  - balises() : position de chaque département
  - infos() : texte d'un département
  - infos_support() : texte d'un support
  - points() : un point par support
- Afficher la carte
  - carte() : carte + points bleus + boutons
  - cadre() : cadre « Informations » à droite
- Tracer les graphiques
  - graphiques() : trace 4 graphiques et les enregistre dans graphiques.png

**PIED : le lancement**

Appel des fonctions dans l'ordre, création des graphiques, puis enregistrement de carte_antennes.html et ouverture dans le navigateur.

## Démarche algorithmique

**1. Lecture des données :**
Lecture des 6 fichiers de l'ANFR avec pandas.

**2. Nettoyage :**
On enlève les doublons, l'outre-mer et les supports sans coordonnées.
Récupération du département avec les 2 premiers chiffres du code INSEE.
Conversion des coordonnées GPS en degrés décimaux pour pouvoir les placer sur la carte.

**3. Liens entre les tables :**
Liaison des tables entre elles, pour chaque installation :
- l'opérateur (Orange, SFR, Bouygues, Free)
- la génération (2G, 3G, 4G ou 5G)
- le département

**4. Calculs :**
Pour chaque département et chaque support, on compte les installations, les antennes, les opérateurs et les générations.
On cherche aussi le support le plus haut du département.

**5. Création de la carte :**
Création de la carte avec folium : un point bleu par support et un bouton par département.
Quand on clique dessus, les infos s'affichent à droite.

**6. Graphiques :**
Création de 4 graphiques en barres avec matplotlib :
- installations par opérateur ;
- installations par génération ;
- top 5 des départements avec le plus de supports ;
- top 5 des types de supports.

Ils sont enregistrés dans graphiques.png et affichés dans le cadre à droite de la carte.

## Contraintes pour les utilisateurs hors groupe

- Python 3 avec les modules **pandas**, **folium** et **matplotlib** :
  `pip install pandas folium matplotlib`
- Les fichiers de l'ANFR sont à télécharger sur data.gouv.fr, page « Données sur les installations radioélectriques de plus de 5 watts » : https://www.data.gouv.fr/datasets/donnees-sur-les-installations-radioelectriques-de-plus-de-5-watts-1
  Il faut prendre le zip des données (fichiers sup_...) et le zip des tables de référence. Pour la SAÉ, nous avons utilisé les fichiers fournis sur UniversiTice.
- Ils doivent être placés dans `data/` et `ref/` avec exactement les noms ci-dessus.
- Une connexion Internet est nécessaire pour afficher le fond de carte.
- Les fichiers sont volumineux : l'exécution peut prendre une à deux minutes.

## Lancer le programme

Depuis le dossier `SAE15` :

```
python carte_antennes.py
```
