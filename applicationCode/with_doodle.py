#Ce fichier contient toutes les fonctions d'intéraction avec le sondage Doodle


from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests
import json
import datetime
import time


#RECUPERATION DES CREANEAUX DOODLE LORS DU PREMIER AJOUT DE CELUI CI

def recup_creneaux(key):
    #1er janvier 1970 en date python : date de référence dans le systeme de date du Doodle
    a = datetime.datetime(1970, 1, 1)

    #clé du sondage
    key = 'uxbhw66spz9eqb9w'

    #url du sondage
    url = 'http://doodle.com/api/v2.0/polls/' + key

    #on stocke le json contenant toutes les informations du sondage dans un dictionnaire appelé l
    r = requests.get(url)
    l = json.loads(r.content)

    #C'est quoi ?
    optionsHash=l["optionsHash"]

    #la liste des options (créneaux) de notre doodle (vide pour l'instant)
    liste_options = []

    #c'est quoi ??
    preferences=[]
    place=[]
    re=0

    #on vérifie si le doodle est deja termine ou non
    #si le doodle est terminé on n'est pas concerné par celui-ci
    try :
        #la clé closed n'est présente que si le sondage est fini
        l["closed"]
        est_final = True

    #si le doodle n'est pas terminé on récupère les options
    except :

        #la clé "options" du dictionnaire l contient les différents créneaux sous la forme
        #{'start': 1540540800000, 'end': 1540558800000, 'startDateTime': 1540540800000, 'endDateTime': 1540558800000, 'available': True}
        for creneau in l["options"]:

            #date et heure de commencement de l'évènement
            secondesEnPlusDebut = int(str(creneau["start"])[0:len(str(creneau["start"]))])

            #date et heure de fin de l'évènement
            secondesEnPlusFin = int(str(creneau["end"])[0:len(str(creneau["end"]))])

            #on ajoute les deux à la liste des options
            optionDebut = a + datetime.timedelta(milliseconds = int(secondesEnPlusDebut)+3600000)
            liste_options.append(optionDebut)
            optionFin = a + datetime.timedelta(milliseconds = int(secondesEnPlusFin)+3600000)
            liste_options.append(optionFin)
            preferences.append(1)
            place.append(re)

            #titre de l'évènement du Doodle
            titre = l["title"]

            #lieu de l'évènement du Doodle
            lieu = l["location"]["name"]

            #description de l'évènement du Doodle
            description = l["description"]

    return [titre, lieu, description, liste_options]

def main():
    print('début')
    sond = recup_creneau('8e6u8t3qeu8b8w3t')
    for s in sond :
        print(s)
