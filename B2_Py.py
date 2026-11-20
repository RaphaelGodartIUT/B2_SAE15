import os #Chemins et dossiers
import pandas as pd #Données en tableaux
import tkinter as tk #Interface graphique
from matplotlib.figure import Figure #Figure du graphique
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #Intégration d'un graphique matplotlib sur Tkinter

def lecture(dossier,fichier,colonnes): #Définition de la fonction de lecture des fichiers
    chemin=dossier+os.sep+fichier #Construction du chemin vers les fichiers
    return pd.read_csv(chemin,sep=";",dtype=str,usecols=colonnes) #Lecture du fichier CSV en sélectionnant les colonnes nécessaires

def nombresss(colonne): #Fonction permettant de convertir une colonne en nombres
    colonne = colonne.str.replace(",",".") #Remplacement des virgules par des points pour faciliter la conversion
    return pd.to_numeric(colonne,errors="coerce") #Conversion des valeurs en nombres et remplacement des erreurs par NaN

def donnees_chargement(): #Fonction permettant de charger et préparer les données pour la carte
    
    global supports
    supports=lecture("data","sup_support.txt",["SUP_ID","COR_NB_DG_LAT","COR_NB_MN_LAT","COR_NB_SC_LAT","COR_NB_DG_LON","COR_NB_MN_LON","COR_NB_SC_LON","COR_CD_EW_LON","COM_CD_INSEE"]) #Chargement du fichier contenant les informations des supports
    supports["departement"]=supports["COM_CD_INSEE"].str[0:2] #Récupération des deux premiers caractères du code INSEE pour identifier le département
    supports=supports.drop_duplicates() #Suppression des lignes en double
    supports=supports[(supports["departement"]!="97")&(supports["departement"]!="98")] #Suppression des départements pas en France directement
    supports["lattitude"]=nombresss(supports["COR_NB_DG_LAT"])+nombresss(supports["COR_NB_MN_LAT"])/60+nombresss(supports["COR_NB_SC_LAT"])/3600 #Conversion des coordonnées de latitude en degrés
    supports["longitude"]=nombresss(supports["COR_NB_DG_LON"])+nombresss(supports["COR_NB_MN_LON"])/60+nombresss(supports["COR_NB_SC_LON"])/3600 #Conversion des coordonnées de longitude en degrés
    ouest=supports["COR_CD_EW_LON"]=="W" #Identification des longitudes à l'ouest de Greenwich
    supports.loc[ouest,"longitude"]=supports.loc[ouest,"longitude"] #Passage des longitudes ouest en valeurs négatives

def balises(): #Ajout de la position de la balise de chaque dép
   
    global dep,lat,lon #variables globales
    dep=[] #Liste des numéros de départements
    lat=[] #Liste des latitudes des balises
    lon=[] #Liste des longitudes des balises
    
    for chaque_departements in sorted(supports["departement"].unique()): #Parcours de chaque département une seule fois et dans l'ordre
        partie=supports[supports["departement"]==chaque_departements] #Sélection des supports du département
        dep.append(chaque_departements) #Ajout du numéro du département
        lat.append(partie["lattitude"].mean()) #Moyenne des latitudes du département = latitude de la balise
        lon.append(partie["longitude"].mean()) #Moyenne des longitudes du département = longitude de la balise

def carte(): #carte des antennes
    
    global plot #Déclaration de plot comme variable globale
    fond=supports.drop_duplicates("SUP_ID") #Conservation d'une seule ligne par identifiant de support
    plot = figure.add_subplot(111) #1ere ligne 1ere colonne 1ere pos
    plot.scatter(fond["longitude"],fond["lattitude"],s=0.3,color="g") #Placement des antennes
    plot.scatter(lon,lat,s=60,color="red",edgecolors="darkred") #Placement des balises des départements
    
    for i in range(len(dep)): #Parcours de chaque balise
        plot.text(lon[i],lat[i]+0.12,dep[i],ha="center",fontsize="6") #Écriture du numéro du département juste au-dessus de sa balise
    plot.set_aspect(1.2) #Proportions de la carte pour ne pas déformer la France
    plot.set_title("Carte de la France") #Titre carte
    plot.set_xlabel("Longitude") #Ajout du nom de x
    plot.set_ylabel("lattitude") #Ajout du nom de y
    canvas.draw() #Actualisation de l'affichage du graphique
    
def fenetre(): #Fenêtre TKINTER
    
    global fenetre, figure, canvas
    fenetre=tk.Tk() #Création de la fenêtre principale
    fenetre.title("Carte Française Des Antennes nG") #Titre
    fenetre.geometry("1920x1080") #Fenêtre tkiner taille
    gauche=tk.Frame(fenetre) #Cadre graphique
    figure = Figure(figsize=(8, 8)) #Taille de la carte
    gauche.pack(side="left",fill="both",expand=True) #Positionnement du cadre et adaptation à la taille de la fenêtre
    canvas=FigureCanvasTkAgg(figure,master=gauche) #Intégration du graphique dans mon tkinter
    canvas.get_tk_widget().pack(fill="both",expand=True) #Affichage du graphique dans mon tkinter

os.chdir(os.path.dirname(os.path.abspath(__file__))) #Définition du dossier du script comme répertoire de travail
donnees_chargement() #Chargement des données
balises() #Départements
fenetre() #Création de la fenêtre
carte() #Dessin de la carte avec les antennes et les balises
fenetre.mainloop() #Garde la fenêtre tkinter ouverte
