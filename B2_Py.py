import os
import pandas as pd
def lire_fichier(chemin):
    print("Lecture depuis ce chemin :",chemin)
    tableau=pd.read_csv(chemin,sep=";",dtype=str)
    print("Nous avons donc :",len(tableau),"lignes et",len(tableau.columns),"colonnes")
    return tableau
def afficher_infos(nom,tableau):
    print("=====",nom,"=====")
    print("Colonnes :")
    for colonne in tableau.columns:
        manquants=tableau[colonne].isna().sum()
        print("",colonne,"- valeurs manquantes :",manquants)
    print("Premières lignes:")
    print(tableau.head(3))
print("CWD (Dossier où nous travaillons) :",os.getcwd())
print("Contenu du dossier :",os.listdir("."))
print("Contenu de data :",os.listdir("data"))
print("Contenu de ref :",os.listdir("ref"))
stations=lire_fichier("data"+os.sep+"sup_station.txt")
supports=lire_fichier("data"+os.sep+"sup_support.txt")
antennes=lire_fichier("data"+os.sep+"sup_antenne.txt")
emetteurs=lire_fichier("data"+os.sep+"sup_emetteur.txt")
exploitants=lire_fichier("ref"+os.sep+"sup_exploitant.txt")
natures=lire_fichier("ref"+os.sep+"sup_nature.txt")
afficher_infos("Stations",stations)
afficher_infos("Supports",supports)
afficher_infos("Antennes",antennes)
afficher_infos("Emetteurs",emetteurs)
afficher_infos("Exploitants",exploitants)
afficher_infos("Natures",natures)
print("Systèmes émetteurs :")
systemes=emetteurs["EMR_LB_SYSTEME"].value_counts()
for nom in systemes.index:
    print("",nom,":",systemes[nom])