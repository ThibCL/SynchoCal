#Ce fichier contient toutes les fonctions d'intéraction avec le sondage Doodle


from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests
import json
import datetime
import time



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


    #la liste des options (créneaux) de notre doodle (vide pour l'instant)
    liste_options = []

    #on vérifie si le doodle est deja termine ou non
    #si le doodle est terminé on n'est pas concerné par celui-ci
    try :
        #la clé closed n'est présente que si le sondage est fini
        l["closed"]
        liste_options_finales = []

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

            #titre du Doodle
            titre = l["title"]

            #lieu du Doodle
            lieu = l["location"]["name"]

            #description du Doodle
            description = l["description"]

    return [titre, lieu, description, liste_options]

def main():
    recup_creneau('dzvsdpkhe534rivt')
