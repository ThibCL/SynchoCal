#Ce fichier contient toutes les fonctions d'intéraction avec le sondage Doodle

from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests
import json
import datetime
import time
import requests as rq




SCOPES = 'https://www.googleapis.com/auth/calendar'

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

url = "https://doodle.com/api/v2.0/polls/"


#Fonction qui permet de créer les Json représentant les évènements correspondants aux dates contenues dans eventdate, et ayant pour titre, lieu et description ceux entrés en argumentself.
#Ce json est écrit sous la forme adaptée à google calendar pour ajouter un evenement.
def conversion(eventdate,titre,lieu,description):
    res=[]
    for ki in range( len(eventdate)//2):

        event2 = {
                      'summary': titre,
                      'location': lieu,
                      'description': description,
                      'start': {
                        'dateTime': eventdate[2*ki],
                        'timeZone': 'Europe/London',
                      },
                      'end': {
                        'dateTime': eventdate[2*ki+1],
                        'timeZone': 'Europe/London',
                      },
                      'recurrence': [
                        'RRULE:FREQ=DAILY;COUNT=1'
                      ],
                      'reminders': {
                        'useDefault': False,
                        'overrides': [
                          {'method': 'email', 'minutes': 24 * 60},
                          {'method': 'popup', 'minutes': 10},
                        ],
                      },
                    }
        res.append(event2)
    return res


#Cette fonction renvoie la liste des évenement à reserver dans le calendrier, la liste des préférences de l'utilisateur (ses disponibilités)
#à envoyer au Doodle et l'optionhash qui est utile pour ecrire dans un doodle. La clé (key) du Doodle est donné en entrée.
def recup_creneaux(key):
    #1er janvier 1970 en date python
    a = datetime.datetime(1970, 1, 1)

    #on stocke le json dans le dictionnaire l
    r = requests.get(url)
    l = json.loads(r.content)

    #nécessaire pour écrire dans le Doodle
    optionsHash=l["optionsHash"]


    #la liste des options (créneaux) de notre doodle (vide pour l'instant)
    liste_options = []

    #la liste préférences est la liste de 0 et/ou 1 qu'il faut envoyer au Doodle pour le remplir
    preferences=[]

    #représente les places des créneaux finaux dans la liste des préférences
    place=[]

    #compteur représentant le nombre de créneaux
    re=0


    #D'abord, on récupère la liste des dates des débuts et des fins (alternées 2 à 2) des évènements du Doodles.
    #On distingue le cas ou le Doodle est fermé ou non

    try:
        #On regarde si le sondage est fermé ou pas
        t=l['closed']

        #Si le sondage est fermé on récupère tous les crénaux qui sont finaux
        for temps in l["options"]:

            try:
                #on vérifie si l'évenement est final
                bool=temps['final']


                #Date et heure de commencement de l'évènement
                secondesEnPlusDebut = int(str(temps["start"])[0:len(str(temps["start"]))])

                #Date et heure de fin de l'évènement
                secondesEnPlusFin = int(str(temps["end"])[0:len(str(temps["end"]))])

                #On ajoute les deux à la liste des options
                optionDebut = a + datetime.timedelta(milliseconds = int(secondesEnPlusDebut)+3600000)
                liste_options.append(optionDebut)
                optionFin = a + datetime.timedelta(milliseconds = int(secondesEnPlusFin)+3600000)
                liste_options.append(optionFin)

                #Au début, on met par défaut que la personne est libre à tous les crénaux finaux
                preferences.append(1)
                #Vu qu'on récupère seulement les crénaux finaux on conserve leur place dans la liste des preferences
                place.append(re)

            except:
                #Si la date n'est pas finale on ajoute 0 aux préférences, et nous n'avons donc pas à nous soucier des dates non-finales
                preferences.append(0)

            re+=1


    except:
        #Si le sondage est toujours ouvert on récupère tous les créneaux du doodle
        for temps in l["options"]:

            #Date et heure de commencement de l'évènement
            secondesEnPlusDebut = int(str(temps["start"])[0:len(str(temps["start"]))])

            #Date et heure de fin de l'évènement
            secondesEnPlusFin = int(str(temps["end"])[0:len(str(temps["end"]))])

            #On ajoute les deux à la liste des options
            optionDebut = a + datetime.timedelta(milliseconds = int(secondesEnPlusDebut)+3600000)
            liste_options.append(optionDebut)
            optionFin = a + datetime.timedelta(milliseconds = int(secondesEnPlusFin)+3600000)
            liste_options.append(optionFin)

            #Par défault on met dans la liste des préférences qu'on est libre à aucun créneaux
            preferences.append(0)

            #On ajoute la place de chaque créneau dans la liste des préference
            place.append(re)
            re+=1



    #On stocke les infos importantes du doodle
    titre = l["title"]
    try :
        lieu = l["location"]["name"]
    except:
        lieu = "Pas de lieu spécifié"
    try:
        description = l["description"]
    except:
        description = "Pas de description spécifiée"

    #On récupère la date actuelle en format adapté aux dates du Doodle
    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indique le temps UTC

    #Nous récupérons les évènements du calendrier sur les créneaux récupérés dans listes_options

    i = 1
    eventdate=[]
    for option in liste_options :

        #si i est pair, c'est une date de début
        if i%2==1 :
            debut=str(option)[0:10]+'T'+str(option)[11:20]+'+01:00'
            i+=1

        #si i est impair c'est une date de fin
        else :
            fin=str(option)[0:10]+'T'+str(option)[11:20]+'+01:00'
            #on récupère les évènement du calendrier se situant entre début et fin (même s'ils commencent ou terminent après)
            events_result = service.events().list(calendarId='primary', timeMin=debut, timeMax=fin).execute()
            events = events_result.get('items', [])

            #Si il n'y a pas d'évènement dans le calendrier à ce créneau, on remplit le calendrier en réservant le créneau et on modifie la liste
            #preference en mettant 1 à la bonne place dans la liste
            if not events:
                eventdate.append(debut)
                eventdate.append(fin)
                preferences[place[i//2-1]]=1


            i+=1
            #on convertit la liste des horaires des créneaux en liste des événements qu'on va envoyé au calendrier
            eventdate2=conversion(eventdate,titre,lieu,description)

    return eventdate2,preferences,optionsHash




def reserve_creneaux(eventdate, key):

    #Liste des évènements réservés avec leurs id respectifs (important pour la suppression)
    eventfinal=[]

    #On parcourt les evenements de eventdate
    for k in eventdate:

        #On reserve le créneaux prévus dans le calendrier
        service.events().insert(calendarId='primary', body=k).execute()

        #On récupère les événements qu'on vient juste de résérver car lorsqu'on insère un evenenement, un id est créé par le calendrier et
        #on en a besoin pour effacer les evenements
        event=service.events().list(calendarId='primary', timeMin=k['start']['dateTime'], timeMax=k['end']['dateTime']).execute()['items']
        j=0

        #La commande précedente renvoie une liste des évenements ayant un moment en commun avec l'intervalle donné, on parcourt donc la liste jusqu'a trouver
        #l'événement qu'on vient d'insérer en comparant les dates de début et de fin
        while event[j]['end']['dateTime']!=k['end']['dateTime'] and event[j]['start']['dateTime']!=k['start']['dateTime']:
            j=j+1

        #On ajoute cet évenement à la liste des evénement. Cette liste est comme eventdate sauf qu'on a les id en plus
        eventfinal.append(event[j])

    return eventfinal




#Cette fonction permet d'effacer du calendrier tous les créneaux reservés précedement à partir du doodle afin de tout recommencer lors d'une mis à jour
def efface(key):
    #On ouvre le fichier qui stock tous les evn réservés
    f=open(key + ".txt" , "r")

    #Et pour chaque ligne on efface l'événement à partir de son id
    for line in f:
        try:
            service.events().delete(calendarId='primary', eventId=eval(line)['id']).execute()
        except:
            #Au cas ou le propriétaire du calendrier à supprimer l'evn à la main
            print('Déja sup')
    f.close()



#Fonction qui permet de mettre à jour les réponses apportés au doodle et les evn réservés, par exemple si le doodle est modifié
def misajour(key,nom_utilisateur):

    #On commence par tout effacer dans le calendrier
    efface(key)

    #on récupère les créneaux ou on est libre
    eventts=recup_creneaux(key)
    #Et enfin on reserve dans le calendrier les créneaux libres
    reserve_creneaux(eventts[0],key)
    #On récupère de la fonction recupcreneaux les préferneces pour les envoyer au doodle
    preferences = eventts[1]

    #Paramètres important pour écrire dans le doodle
    participantKey = "et5qinsv"
    optionsHash = eventts[2]

    #On récupère tout le json du doodle pour retouver l'id de la personne considéré par la mise à jour
    l=rq.get('https://doodle.com/api/v2.0/polls/dzvsdpkhe534rivt')
    ri=json.loads(l.content)
    li=0

    #on attend de tomber sur le participant qui a le même nom que celui qui a le calendrier
    while(ri['participants'][li]['name']!=nom_utilisateur):
        li+=1

    #On créé le json à envoyer au doodle pour modifier les choix de l'utilisateur
    envoi = {"id":ri['participants'][li]['id'],"name" : nom_utilisateur,
             "optionsHash" : optionsHash, "participantKey": participantKey,
             "preferences" : preferences}

    #Url nécesssaire pour l'envoi des infos
    url2=url+"/participants/"+str(ri['participants'][li]['id'])
    #requête put qui modifie un post précedent
    ra = rq.put(url2, json = envoi)
    print("Sondage"+key+"mis à jour")
