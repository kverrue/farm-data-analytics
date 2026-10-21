from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.db import get_db
bp = Blueprint("index", __name__)


# Recherche des données dans les tables sql
def Pourcentages():
    '''
    pre:/
    post: pourcentage naissances par jour du cycle lunaire
    '''

    db = get_db()

    def makeDates(Jfrom, Mfrom, Yfrom, Jto, Mto, Yto):
        '''
        pre: Jfrom, Mfrom, Yfrom, Jto, Mto, Yto des integer
        post: calendrier lunaire
        '''
        jours = Jfrom
        mois = Mfrom
        annee = Yfrom

        dates = {}
        
        dates[f"{jours:02}/{mois:02}/{annee}"] = 0
        while not (jours == Jto and mois == Mto and annee == Yto):
            jours += 1
            if mois == 2:
                if annee%4 != 0 and jours == 29:
                    jours = 1
                    mois += 1
                elif annee%4 == 0 and jours == 30:
                    jours = 1
                    mois += 1
            elif mois%2 == 1:
                if mois <= 7 and jours == 32:
                    jours = 1
                    mois += 1
                if mois > 7 and jours == 31:
                    jours = 1
                    mois += 1
            elif mois%2 == 0:
                if mois <= 7 and jours == 31:
                    jours = 1
                    mois += 1
                if mois > 7 and jours == 32:
                    jours = 1
                    mois += 1
            
            if mois == 13:
                mois = 1
                annee += 1
            
            dates[f"{jours:02}/{mois:02}/{annee}"] = 0
        return dates

    Dates = makeDates(int(tuple(db.execute("select date from velages"))[0][0][0:2]), int(tuple(db.execute("select date from velages"))[0][0][3:5]), int(tuple(db.execute("select date from velages"))[0][0][6:]), int(tuple(db.execute("select date from velages"))[-1][0][0:2]), int(tuple(db.execute("select date from velages"))[-1][0][3:5]), int(tuple(db.execute("select date from velages"))[-1][0][6:]))

    for born in db.execute("select date from velages"):
        Dates[born[0]] += 1

    cycle = []
    for a in range(28):
        cycle.append(0)

    n = 0
    for c in range(0, len(Dates)-28, 29):
        tnc = 0
        for t in range(28):
            tnc += list(Dates.items())[c+t][1] #tnc: Total de naissance du cycle
        if tnc != 0:
            for i in range(28):
                cycle[i] += list(Dates.items())[c+i][1]*(100/tnc)
        n += 1

    for m in range(len(cycle)):
        cycle[m] = round(cycle[m]/n, 2)

    Somme = 0
    for i in cycle:
        Somme += i
    
    return cycle

# Total de vaches par famille
def TotalDeVachesDansFamille():
  '''
  pre:/
  post: renvoie un dictionnaire avec le nombre(value) total de vaches par famille(key)
  '''
  db = get_db()
  familles={}
  for id_famille in db.execute("SELECT id FROM familles"):
    count=0
    for vache,famille in db.execute("SELECT id, famille_id FROM animaux "):
      if famille == id_famille:
        count += 1
        familles[famille]=count
  return familles
# Le nombre de vaches mortes prématurément par famille
def TotalDeVachesMortesParFamille():
  '''
  pre:/
  post: renvoie un dictionnaire avec le nombre(value) de vaches mortes par famille(key)
  '''
  db = get_db()
  familles = {}
  for id_famille in db.execute("SELECT id FROM familles"):
    count = 0
    for vache,famille in db.execute("SELECT id, famille_id FROM animaux WHERE decede= 1 "):
      if famille == id_famille:
        count += 1
        familles[famille] = count
  return familles
# Nombre de vaches vivantes par famille
def TotalDeVachesVivantesParFamille():
  '''
  pre:/
  post: renvoie un dictionnaire avec le nombre(value) de vaches vivantes par famille(key)
  '''
  VachesVivantes={}
  for famille in TotalDeVachesDansFamille().keys():
    VachesVivantes[famille]= int(TotalDeVachesDansFamille().values()) - int(TotalDeVachesMortesParFamille().values())
  return VachesVivantes

def totalveauxmortnes():
    '''
    pre:/
    post: renvoie un dictionnaire avec le nombre de veaux morts-nés par mois
    '''

    db = get_db()

    nombre_mort_nes={'01':0,'02':0,'03':0,'04':0,'05':0,'06':0,'07':0,'08':0,'09':0,'10':0,'11':0,'12':0,}
    for ligne in db.execute("SELECT animaux.id, animaux.mort_ne, velages.date from animaux INNER JOIN velages ON animaux.id = velages.id WHERE animaux.mort_ne <>'8';"):
        nombre_mort_nes[ligne[2][3:5]]+=1
    
    return nombre_mort_nes

def Velage():
    '''
    pre:/
    post: renvoie un dictionnaire avec le nombre de velages par année
    '''
    db = get_db()
    data = list(db.execute("SELECT mere_id, date FROM velages"))
    dico={}
    annee={}
    for x in data:       # on crée 2 dictionnaires avec le nombre de velages par années
        if dico.get(x[0],None) == None:
            dico[x[0]]=1
        else:
            dico[x[0]]+=1
        if annee.get(x[1][-4:],None) == None:
            annee[x[1][-4:]]={dico[x[0]]:1}
        
        else:
            if annee[x[1][-4:]].get(dico[x[0]],None) == None:
                annee[x[1][-4:]][dico[x[0]]]=1
            else:
                annee[x[1][-4:]][dico[x[0]]]+=1

    for a in annee:        #on récupère les donnés pour chaque année
        for i in range(1,8):
            if annee[a].get(i,None) == None:
                annee[a][i]=0
    
    #on renvoie le dictionnaire avec les données du nombre de velages par an
    return annee 




@bp.route("/")
def index():
    '''
    pre:/
    post: relie les valeurs extraites des extractor.py à une valeur
          qui sera associée aux graphes dans le fichier interfacefinale2.html
    '''
    PourcentageParCycle= Pourcentages() # [40, 50, 10, 47, 80, 2, 49, 56, 57, 13, 50, 56, 67, 15, 67, 22, 44, 66, 88, 56, 8, 4, 10, 50, 60, 5, 6, 8]

    mortes =  list(TotalDeVachesMortesParFamille().values()) #[41,50,5,20,40,80,50,18,34,45,150]
    vivantes=  list(TotalDeVachesVivantesParFamille().values()) #[160,305,200,100,120,300,79,179,150,230,20]
    familles= list(TotalDeVachesVivantesParFamille().keys()) #['famille1','famille2','famille3','famille4','famille5','famille6','famille7','famille8','famille9','famille10','famille11']
    mortes   = [41,50,5,20,40,80,50,18,34,45,150]
    vivantes = [160,305,200,100,120,300,79,179,150,230,20]
    familles = ['famille1','famille2','famille3','famille4','famille5','famille6','famille7','famille8','famille9','famille10','famille11']

    deces= list(totalveauxmortnes().values())  #[40,50,10,47,30,2,49,56,57,13,50,10]

    VelageX =['1986','1990','1998','2000','2001','2002','2007', '2010','2019','2020']
    VelageS = [10,30,40,20,50,15,18,60,70,12]
    Annee = Velage()

    for a in Annee:
        for i in range(1, 8):
            if i == 1:
                VelageX.append("{}: {}er velage(s)".format(a, i))
            else:
                VelageX.append("{}: {}eme velage(s)".format(a, i))
    VelageS = []
    for a in Annee:
        for i in range(1, 8):
            VelageS.append(Annee[a][i])

    return render_template('index.html', PourcentageVelagePleineLune=PourcentageParCycle, m=mortes, v=vivantes,f=familles, n=deces, VelageX=VelageX, VelageS=VelageS)