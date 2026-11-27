import os #To find our files and folders
import webbrowser #Opens map in browser
import pandas as pd #Data in the board
import folium #Interactive Map
import matplotlib.pyplot as plt #Graphics !
from folium.plugins import MarkerCluster #Group points

GENERATIONS={"GSM 900":"2G","GSM 1800":"2G","UMTS 900":"3G","UMTS 2100":"3G", #2/3G Systems
             "LTE 700":"4G","LTE 800":"4G","LTE 900":"4G","LTE 1800":"4G","LTE 2100":"4G","LTE 2600":"4G", #4G Systems
             "5G NR 700":"5G","5G NR 2100":"5G","5G NR 3500":"5G"} #5G Systems
OPERATEURS=["ORANGE","SFR","BOUYGUES TELECOM","FREE MOBILE"] #Mobile Operators
STYLE_DE_LA_CARTE_SATELLITE_BEAU="https://data.geopf.fr/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=ORTHOIMAGERY.ORTHOPHOTOS&STYLE=normal&FORMAT=image/jpeg&TILEMATRIXSET=PM_0_19&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}" #Satellite Images for MAP

def lecture(dossier,fichier,colonnes): #Read files function definition
    chemin=dossier+os.sep+fichier #Path to our files
    return pd.read_csv(chemin,sep=";",dtype=str,usecols=colonnes) #Reading CSV files using the line beforehand

def nombresss(colonne): #Function : columns = numbers
    colonne=colonne.str.replace(",",".") #Replacing "," by "." for easier calculations
    return pd.to_numeric(colonne,errors="coerce") #Values become numbers and errors become NaN

def donnees_chargement(): #Loading Dat

    global supports, stations, generations, antennes #These will become global and can be used in other functions
    supports=lecture("data","sup_support.txt",["SUP_ID","STA_NM_ANFR","NAT_ID","COR_NB_DG_LAT","COR_NB_MN_LAT","COR_NB_SC_LAT","COR_NB_DG_LON","COR_NB_MN_LON","COR_NB_SC_LON","COR_CD_EW_LON","SUP_NM_HAUT","ADR_LB_ADD1","ADR_LB_LIEU","COM_CD_INSEE"]) #Support Data
    stations=lecture("data","sup_station.txt",["STA_NM_ANFR","ADM_ID"]) #Loading installations with their operator
    antennes=lecture("data","sup_antenne.txt",["AER_ID","SUP_ID"]) #Loading antennas and their supports
    emetteurs=lecture("data","sup_emetteur.txt",["STA_NM_ANFR","EMR_LB_SYSTEME"]) #Loading transmitters with their system (GSM, LTE, 5G,...........)
    exploitants=lecture("ref","sup_exploitant.txt",["ADM_ID","ADM_LB_NOM"]) #Loading operators name
    natures=lecture("ref","sup_nature.txt",["NAT_ID","NAT_LB_NOM"]) #Loading support name (water castle, other stuff,...)

    supports["departement"]=supports["COM_CD_INSEE"].str[0:2] #Taking fist two numbers for departments
    supports=supports.drop_duplicates() #Doubles are now deleted
    supports=supports[(supports["departement"]!="97")&(supports["departement"]!="98")] #Deleting other departments that are in outer sea
    supports["lattitude"]=nombresss(supports["COR_NB_DG_LAT"])+nombresss(supports["COR_NB_MN_LAT"])/60+nombresss(supports["COR_NB_SC_LAT"])/3600 #Latitude coordinates in degrees
    supports["longitude"]=nombresss(supports["COR_NB_DG_LON"])+nombresss(supports["COR_NB_MN_LON"])/60+nombresss(supports["COR_NB_SC_LON"])/3600 #Longitude coordinates in degrees

    ouest=supports["COR_CD_EW_LON"]=="W" #longitudes

    supports.loc[ouest,"longitude"]=-supports.loc[ouest,"longitude"] #W in negative
    supports["hauteur"]=nombresss(supports["SUP_NM_HAUT"]) #Height of the support
    supports=supports.merge(natures,on="NAT_ID",how="left") #Adding name of the support
    supports["adresse"]=supports["ADR_LB_ADD1"].fillna(supports["ADR_LB_LIEU"]) #Shows address of the support, if the thing is empty, it replaces itself by the location
    supports=supports.dropna(subset=["lattitude","longitude"]) #Deleting supports without coordinates

    stations=stations.merge(exploitants,on="ADM_ID",how="left") #Operator's name to every stations
    stations=stations.merge(supports[["STA_NM_ANFR","departement"]].drop_duplicates("STA_NM_ANFR"),on="STA_NM_ANFR") #Departement's name to every stations

    emetteurs["generation"]=emetteurs["EMR_LB_SYSTEME"].map(GENERATIONS) #Transmitter's system translation to nG generation
    generations=emetteurs[emetteurs["generation"].notna()] #Keeping transmitters with known positions
    generations=generations[["STA_NM_ANFR","generation"]].drop_duplicates() #One line per station and generation
    generations=generations.merge(stations[["STA_NM_ANFR","departement"]],on="STA_NM_ANFR") #Adding every station's departments

    antennes=antennes.drop_duplicates("AER_ID") #A single line per antenna
    antennes=antennes.merge(supports[["SUP_ID","departement"]].drop_duplicates("SUP_ID"),on="SUP_ID") #Adding department of every antennas thanks to its support

def balises(): #Adding position of each department

    global dep,lat,lon
    dep=[] #List of department numbers
    lat=[] #List of positions in latitude
    lon=[] #List of positions in longitude

    grouped = supports.groupby("departement")[["lattitude", "longitude"]].mean().reset_index() #Tracking every department, once, in order
    dep = grouped["departement"].tolist() #Adding number of dpt
    lat = grouped["lattitude"].tolist() #Average of latitude of the department = latitude of the point on the MAP
    lon = grouped["longitude"].tolist() #Average of longitude of the department = longitude of the point on the MAP

def infos(numero): #Fonction that writes information of each department

    supports_dep=supports[supports["departement"]==numero].drop_duplicates("SUP_ID") #Supports of the department, once each
    stations_dep=stations[stations["departement"]==numero] #Stations of the departement
    generations_dep=generations[generations["departement"]==numero] #Genenration of stations of each departments

    texte="DÉPARTEMENT "+numero+"<br>" #Numéro département
    texte=texte+"Installations : "+str(len(stations_dep))+"<br>" #Number of installations
    texte=texte+"Supports : "+str(len(supports_dep))+"<br>" #Number of supports
    texte=texte+"Antennes : "+str(len(antennes[antennes["departement"]==numero]))+"<br><br>" #Number of antennas

    texte=texte+"Installations par opérateur :<br>" #Title of operators part
    for operateur in OPERATEURS:
        nombre=len(stations_dep[stations_dep["ADM_LB_NOM"]==operateur]) #Number of stations of this operator in this department
        texte=texte+""+operateur+":"+str(nombre)+"<br>" #Adding line of operator

    texte=texte+"<br>Installations par génération :<br>" #Title of the generationssss part
    for generation in ["2G","3G","4G","5G"]: 
        nombre=len(generations_dep[generations_dep["generation"]==generation]) #Number of stations of this generation in the department
        texte=texte+""+generation+":"+str(nombre)+"<br>" #Adding line of generation

    hauteurs_ok=supports_dep[(supports_dep["hauteur"]>0)&(supports_dep["hauteur"]<=300)] #Supports with realistic height
    if len(hauteurs_ok)>0: #If there's atleast one support
        plus_haut=hauteurs_ok.sort_values("hauteur").iloc[-1] #Sort by height and taking the last one
        texte=texte+"<br>Support le plus haut :<br>" #Title of highest support
        texte=texte+""+str(plus_haut["NAT_LB_NOM"])+" de "+str(plus_haut["hauteur"])+" m<br>" #Type and height of said support
        texte=texte+""+str(plus_haut["adresse"])+"<br>" #Address of support
        texte=texte+"commune INSEE "+plus_haut["COM_CD_INSEE"]+"<br>" #Postal Code
    return texte

def infos_support(ligne): #Function to show the informations of a support

    texte="SUPPORT "+str(ligne["SUP_ID"])+"<br>" #Number of supports
    texte=texte+"Installations : "+str(ligne["installations"])+"<br>" #Number of installations
    texte=texte+"Antennes : "+str(ligne["antennes"])+"<br><br>" #Number of antennas

    texte=texte+"Installations par opérateur :<br>" #Title of the operator part
    for operateur in OPERATEURS: 
        texte=texte+""+operateur+":"+str(ligne[operateur])+"<br>" #Adding operator line

    texte=texte+"<br>Installations par génération :<br>" #Title of the generation part
    for generation in ["2G","3G","4G","5G"]:
        texte=texte+""+generation+":"+str(ligne[generation])+"<br>" #Adding line of the generation

    texte=texte+"<br>Support :<br>" #Title of the support part
    texte=texte+""+str(ligne["NAT_LB_NOM"])+" de "+str(ligne["hauteur"])+" m<br>" #Type and height of support
    texte=texte+""+str(ligne["adresse"])+"<br>" #Support's address
    texte=texte+"commune INSEE "+str(ligne["COM_CD_INSEE"])+"<br>" #INSEE city code
    return texte #Sending back text

def points(): #Preparation of each points, with a single point meaning it's a support

    global liste_points #Global variable stuff
    fond=supports.drop_duplicates("SUP_ID") #A single line for each identifier of every support
    liens=supports[["SUP_ID","STA_NM_ANFR"]].drop_duplicates() #Which station is on which support.
    liens_operateurs=liens.merge(stations[["STA_NM_ANFR","ADM_LB_NOM"]],on="STA_NM_ANFR") #Adding operator to each station
    liens_generations=liens.merge(generations[["STA_NM_ANFR","generation"]],on="STA_NM_ANFR") #Adding generations of each support

    fond["installations"]=fond["SUP_ID"].map(liens["SUP_ID"].value_counts()).fillna(0).astype(int) #Number of installations per support
    fond["antennes"]=fond["SUP_ID"].map(antennes["SUP_ID"].value_counts()).fillna(0).astype(int) #Number of antennas per support
    for operateur in OPERATEURS: 
        partie=liens_operateurs[liens_operateurs["ADM_LB_NOM"]==operateur] #Stations of this operator
        fond[operateur]=fond["SUP_ID"].map(partie["SUP_ID"].value_counts()).fillna(0).astype(int) #Number of stations of this operation per support
    for generation in ["2G","3G","4G","5G"]: 
        partie=liens_generations[liens_generations["generation"]==generation] #Stations of this generation
        fond[generation]=fond["SUP_ID"].map(partie["SUP_ID"].value_counts()).fillna(0).astype(int) #Number of stations of this generation per support
    fond=fond.fillna("inconnu") #Empty spots are now "inconnu"

    liste_points=[] #List of points
    for ligne in fond.to_dict("records"): #each ligne in fond.to_dict
        point={"type":"Feature","geometry":{"type":"Point","coordinates":[ligne["longitude"],ligne["lattitude"]]},"properties":{"texte":infos_support(ligne)}} #Creates a GeoJSON Feature for maps
        liste_points.append(point) #Adding point to the list

def carte(): #Map of antennas

    global plan, les_points
    plan=folium.Map(location=[45.5,1.4],zoom_start=6,tiles=None,width="70%",prefer_canvas=True) #Map and settings we've chosen, Courville-Sur-Eure is base location
    folium.TileLayer(STYLE_DE_LA_CARTE_SATELLITE_BEAU,attr="Carte Satellite").add_to(plan) #Chosing map style

    cluster = MarkerCluster().add_to(plan)
    les_points=folium.GeoJson({"type":"FeatureCollection","features":liste_points}, #Every support points
    marker=folium.CircleMarker(radius=4,color="#00e5ff",opacity=0.5,fill_opacity=0.3,fill_color="#00e5ff",fill="true")) #Points style
    les_points.add_to(cluster) #Adding points to map

    for i in range(len(dep)): #Traveling across every departments
        bouton="<button style='background-color:#1e293b;color:#38bdf8;padding:5px 10px;font-weight:bold;cursor:pointer;' onclick=\"document.getElementById('infos').innerHTML=document.getElementById('dep"+dep[i]+"').innerHTML\">"+dep[i]+"</button>" #Style of button department 
        folium.Marker([lat[i],lon[i]],icon=folium.DivIcon(html=bouton,icon_size=(15,7),icon_anchor=(15,11))).add_to(plan) #PAdding button to the department thing with size and anchor chosen

def cadre(): #Informations tab

    page="<div style='position:absolute;top:0;left:71%'>" #Positioning the tab at the right of the map
    page=page+"<h2>Informations</h2>" #Tab title
    page=page+"<div id='infos'>Cliquez sur un numéro de département ou sur un point</div>" #Text showing informations
    page=page+"<img src='graphiques.png' style='width:100%'>" #Allows us to add the graphiques.png image to the informations tab
    page=page+"</div>" #End of tab
    for i in range(len(dep)): #Traveling across every departments
        page=page+"<div id='dep"+dep[i]+"' hidden>"+infos(dep[i])+"</div>" #Hidden department text on the
    page=page+"<script>document.addEventListener('DOMContentLoaded',function(){"+les_points.get_name()+".on('click',function(clic){document.getElementById('infos').innerHTML=clic.layer.feature.properties.texte})})</script>" #Allows to click on the dot to show the informations
    plan.get_root().html.add_child(folium.Element(page)) #Adding texts to tab

def graphiques():
    plt.figure(figsize=(8,16)) #Size of the entire figure (width, height in inches)
    plt.subplot(4,1,1) #4 rows, 1 column, 1st place
    
    op_counts = stations["ADM_LB_NOM"].value_counts()
    operateurssss = [op_counts.get(operateur, 0) for operateur in OPERATEURS] #List to store the station counts for each operator
    plt.bar(OPERATEURS,operateurssss) #Creates the bar chart (does not display it yet)
    plt.title("Installations par operateur") #Title
    
    plt.subplot(4,1,2) #4 rows, 1 column, 2nd place
    gens=["2G","3G","4G","5G"] #List of network generations
    
    gen_counts = generations["generation"].value_counts()
    xG = [gen_counts.get(i, 0) for i in gens] #List to store the count for each generation (1,2,3,4,5)
    plt.bar(gens,xG) #Creates the bar chart for generations
    plt.title("nb Installations par generation") #Title
    
    plt.subplot(4,1,3) #4 rows, 1 column, 3rd place
    top_dep=supports.drop_duplicates("SUP_ID")["departement"].value_counts().head(5) #Removes duplicate supports, counts by department, keeps top 5
    plt.bar(top_dep.index,top_dep.values) #Creates the bar chart
    plt.title("Top 5 departements en fonction de leurs supports") #Title
    
    plt.subplot(4,1,4) #4 rows, 1 column, 4th place
    top_nat=supports.drop_duplicates("SUP_ID")["NAT_LB_NOM"].value_counts().head(5) #Removes duplicate supports, counts by support type, keeps top 5
    plt.bar(top_nat.index,top_nat.values) #Creates the bar chart
    plt.title("Top 5 types de supports") #Title
    
    plt.savefig("graphiques.png") #Saves the entire figure as a PNG image
    plt.close() #Closes the figure to free up memory

os.chdir(os.path.dirname(os.path.abspath(__file__))) #CD is now where the script is
donnees_chargement() #Loading Data
balises() #Departments
points() #Supports points
carte() #Map with departments and antennas
cadre() #Creating the information stuff tab
graphiques()
plan.save("carte_antennes.html") #Saving said map in an html file
webbrowser.open("file://"+os.path.abspath("carte_antennes.html")) #Opening the map in web browser