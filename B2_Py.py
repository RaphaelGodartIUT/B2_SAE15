import os #Chemins et dossiers
import pandas as pd #Données en tableaux
import tkinter as tk #Interface graphique
from matplotlib.figure import Figure #Figure du graphique
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg #Intégration d'un graphique matplotlib sur Tkinter

GENERATIONS={"GSM 900":"2G","GSM 1800":"2G","UMTS 900":"3G","UMTS 2100":"3G", #Systèmes 2G & 3G
             "LTE 700":"4G","LTE 800":"4G","LTE 900":"4G","LTE 1800":"4G","LTE 2100":"4G","LTE 2600":"4G", #Systèmes 4G
             "5G NR 700":"5G","5G NR 2100":"5G","5G NR 3500":"5G"} #Systèmes 5G
OPERATEURS=["ORANGE","SFR","BOUYGUES TELECOM","FREE MOBILE"] #Opérateurs mobiles

def lecture(dossier,fichier,colonnes): #Définition de la fonction de lecture des fichiers
    chemin=dossier+os.sep+fichier #Construction du chemin vers les fichiers
    return pd.read_csv(chemin,sep=";",dtype=str,usecols=colonnes) #Lecture du fichier CSV en sélectionnant les colonnes nécessaires

def nombresss(colonne): #Fonction permettant de convertir une colonne en nombres
    colonne = colonne.str.replace(",",".") #Remplacement des virgules par des points pour faciliter la conversion
    return pd.to_numeric(colonne,errors="coerce") #Conversion des valeurs en nombres et remplacement des erreurs par NaN

def donnees_chargement(): #Fonction permettant de charger et préparer les données pour la carte

    global supports, stations, generations, antennes #Déclaration des tableaux comme variables globales
    supports=lecture("data","sup_support.txt",["SUP_ID","STA_NM_ANFR","NAT_ID","COR_NB_DG_LAT","COR_NB_MN_LAT","COR_NB_SC_LAT","COR_NB_DG_LON","COR_NB_MN_LON","COR_NB_SC_LON","COR_CD_EW_LON","SUP_NM_HAUT","ADR_LB_ADD1","ADR_LB_LIEU","COM_CD_INSEE"]) #Chargement du fichier contenant les informations des supports
    stations=lecture("data","sup_station.txt",["STA_NM_ANFR","ADM_ID"]) #Chargement des stations (installations) avec leur exploitant
    antennes=lecture("data","sup_antenne.txt",["AER_ID","SUP_ID"]) #Chargement des antennes avec le support sur lequel elles sont posées
    emetteurs=lecture("data","sup_emetteur.txt",["STA_NM_ANFR","EMR_LB_SYSTEME"]) #Chargement des émetteurs avec leur système (GSM, LTE, 5G...)
    exploitants=lecture("ref","sup_exploitant.txt",["ADM_ID","ADM_LB_NOM"]) #Chargement du nom de chaque exploitant
    natures=lecture("ref","sup_nature.txt",["NAT_ID","NAT_LB_NOM"]) #Chargement du nom de chaque type de support (pylône, château d'eau...)
    
    supports["departement"]=supports["COM_CD_INSEE"].str[0:2] #Récupération des deux premiers caractères du code INSEE pour identifier le département
    supports=supports.drop_duplicates() #Suppression des lignes en double
    supports=supports[(supports["departement"]!="97")&(supports["departement"]!="98")] #Suppression des départements pas en France directement
    supports["lattitude"]=nombresss(supports["COR_NB_DG_LAT"])+nombresss(supports["COR_NB_MN_LAT"])/60+nombresss(supports["COR_NB_SC_LAT"])/3600 #Conversion des coordonnées de latitude en degrés
    supports["longitude"]=nombresss(supports["COR_NB_DG_LON"])+nombresss(supports["COR_NB_MN_LON"])/60+nombresss(supports["COR_NB_SC_LON"])/3600 #Conversion des coordonnées de longitude en degrés
    
    ouest=supports["COR_CD_EW_LON"]=="W" #longitudes
    
    supports.loc[ouest,"longitude"]=-supports.loc[ouest,"longitude"] #Passage des longitudes ouest en valeurs négatives
    supports["hauteur"]=nombresss(supports["SUP_NM_HAUT"]) #Conversion de la hauteur du support en nombre
    supports=supports.merge(natures,on="NAT_ID",how="left") #Ajout du nom du type de support grâce à son identifiant
    supports["adresse"]=supports["ADR_LB_ADD1"].fillna(supports["ADR_LB_LIEU"]) #Adresse du support, ou le nom du lieu si l'adresse est vide

    stations=stations.merge(exploitants,on="ADM_ID",how="left") #Ajout du nom de l'opérateur à chaque station
    stations=stations.merge(supports[["STA_NM_ANFR","departement"]].drop_duplicates("STA_NM_ANFR"),on="STA_NM_ANFR") #Ajout du département de chaque station

    emetteurs["generation"]=emetteurs["EMR_LB_SYSTEME"].map(GENERATIONS) #Traduction du système de l'émetteur en génération (2G, 3G, 4G, 5G)
    generations=emetteurs[emetteurs["generation"].notna()] #Conservation des émetteurs dont la génération est connue
    generations=generations[["STA_NM_ANFR","generation"]].drop_duplicates() #Une seule ligne par station et par génération
    generations=generations.merge(stations[["STA_NM_ANFR","departement"]],on="STA_NM_ANFR") #Ajout du département de chaque station

    antennes=antennes.drop_duplicates("AER_ID") #Une seule ligne par antenne
    antennes=antennes.merge(supports[["SUP_ID","departement"]].drop_duplicates("SUP_ID"),on="SUP_ID") #Ajout du département de chaque antenne grâce à son support

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

def infos(numero): #Fonction qui écrit le texte d'informations d'un département

    supports_dep=supports[supports["departement"]==numero].drop_duplicates("SUP_ID") #Supports du département, une seule fois chacun
    stations_dep=stations[stations["departement"]==numero] #Stations du département
    generations_dep=generations[generations["departement"]==numero] #Générations des stations du département

    texte="DÉPARTEMENT ",numero,"\n" #Numéro département
    texte=texte+"------------------------------\n" #Ligne pour le flooow
    texte=texte+"Installations : "+str(len(stations_dep))+"\n" #Nombre d'installations
    texte=texte+"Supports : "+str(len(supports_dep))+"\n" #Nombre de supports
    texte=texte+"Antennes : "+str(len(antennes[antennes["departement"]==numero]))+"\n\n" #Nombre d'antennes

    texte=texte+"Installations par opérateur :\n" #Titre de la partie opérateurs
    for operateur in OPERATEURS: #On parcourt chaque opérateur...
        nombre=len(stations_dep[stations_dep["ADM_LB_NOM"]==operateur]) #Nombre de stations de cet opérateur dans le département
        texte=texte+""+operateur+":"+str(nombre)+"\n" #Ajout de la ligne de l'opérateur

    texte=texte+"\nInstallations par génération :\n" #Titre de la partie générations
    for generation in ["2G","3G","4G","5G"]: #Parcours de chaque génération
        nombre=len(generations_dep[generations_dep["generation"]==generation]) #Nombre de stations de cette génération dans le département
        texte=texte+""+generation+":"+str(nombre)+"\n" #Ajout de la ligne de la génération

    hauteurs_ok=supports_dep[(supports_dep["hauteur"]>0)&(supports_dep["hauteur"]<=300)] #Supports avec une hauteur réaliste (entre 0 et 300 m)
    if len(hauteurs_ok)>0: #S'il reste au moins un support
        plus_haut=hauteurs_ok.sort_values("hauteur").iloc[-1] #Tri par hauteur et récupération du dernier = le plus haut
        texte=texte+"\nSupport le plus haut :\n" #Titre de la partie support le plus haut
        texte=texte+""+str(plus_haut["NAT_LB_NOM"])+" de "+str(plus_haut["hauteur"])+" m\n" #Type et hauteur du support
        texte=texte+""+str(plus_haut["adresse"])+"\n" #Adresse du support
        texte=texte+"commune INSEE "+plus_haut["COM_CD_INSEE"]+"\n" #Code INSEE de la commune (code postal)
    return texte #Renvoi du texte complet

def clic_balise(clic): #Fonction appelée quand on clique sur une balise

    position=clic.ind[0] #Position de la balise cliquée dans la liste
    numero=dep[position] #Numéro du département de cette balise
    label_infos.config(text=infos(numero)) #Affichage des informations du département dans le cadre de droite

def carte(): #carte des antennes

    global plot #Déclaration de plot comme variable globale
    fond=supports.drop_duplicates("SUP_ID") #Conservation d'une seule ligne par identifiant de support
    plot=figure.add_subplot(111) #1ere ligne 1ere colonne 1ere pos
    plot.scatter(fond["longitude"],fond["lattitude"],s=0.3,color="g") #Placement des antennes
    plot.scatter(lon,lat,s=60,color="red",edgecolors="darkred") #Placement des balises des départements
    plot.collections[-1].set_picker(True) #Rend les balises cliquables

    for i in range(len(dep)): #Parcours de chaque balise
        plot.text(lon[i],lat[i]+0.12,dep[i],ha="center",fontsize="8",weight="bold") #Écriture du numéro du département juste au-dessus de sa balise
    plot.set_aspect(1.2) #Proportions de la carte pour ne pas déformer la France
    plot.set_title("Carte de la France") #Titre carte
    plot.set_xlabel("Longitude") #Ajout du nom de x
    plot.set_ylabel("lattitude") #Ajout du nom de y
    canvas.draw() #Actualisation de l'affichage du graphique

def fenetre(): #Fenêtre TKINTER

    global fenetre, figure, canvas
    global label_infos #Déclaration du texte d'informations comme variable globale
    fenetre=tk.Tk() #Création de la fenêtre principale
    fenetre.title("Carte Française Des Antennes nG") #Titre
    fenetre.geometry("1000x1000") #Fenêtre tkiner taille
    gauche=tk.Frame(fenetre) #Cadre graphique
    figure=Figure(figsize=(8, 8)) #Taille de la carte
    gauche.pack(side="left",fill="both",expand=True) #Positionnement du cadre et adaptation à la taille de la fenêtre
    canvas=FigureCanvasTkAgg(figure,master=gauche) #Intégration du graphique dans mon tkinter
    canvas.get_tk_widget().pack(fill="both",expand=True) #Affichage du graphique dans mon tkinter
    canvas.mpl_connect("pick_event",clic_balise) #Appel de clic_balise quand on clique sur une balise
    droite=tk.Frame(fenetre,padx=10,pady=10) #Cadre des informations
    droite.pack(side="right",fill="y") #Positionnement du cadre à droite de la fenêtre
    tk.Label(droite,text="Informations",font=("Arial",14,"bold")).pack(anchor="w") #Titre du cadre
    label_infos=tk.Label(droite,text="Cliquez sur une balise rouge",justify="left",font=("Consolas",10)) #Texte qui affichera les informations du département
    label_infos.pack(anchor="w") #Affichage du texte dans le cadre

os.chdir(os.path.dirname(os.path.abspath(__file__))) #Définition du dossier du script comme répertoire de travail
donnees_chargement() #Chargement des données
balises() #Départements
fenetre() #Création de la fenêtre
carte() #Dessin de la carte avec les antennes et les balises
fenetre.mainloop() #Garde la fenêtre tkinter ouverte
