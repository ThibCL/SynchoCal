from __future__ import print_function
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
import requests
import json
import datetime
import time
import requests as rq


#RECUPARATION DES CRENEAUX DU DOODLE



#RECUPERATION DES DISPONIBILITES DE L'UTILISATEUR SUR CES CRENEAUX

# If modifying these scopes, delete the file token.json.
SCOPES = 'https://www.googleapis.com/auth/calendar'

store = file.Storage('token.json')
creds = store.get()
if not creds or creds.invalid:
    flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
    creds = tools.run_flow(flow, store)
service = build('calendar', 'v3', http=creds.authorize(Http()))

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


def recupcreneaux( url, key):
    #1er janvier 1970 en date python
    a = datetime.datetime(1970, 1, 1)



    #on stocke le json dans le dictionnaire l
    r = requests.get(url)
    l = json.loads(r.content)
    optionsHash=l["optionsHash"]


    #la liste des options (créneaux) de notre doodle (vide pour l'instant)
    liste_options = []
    preferences=[]
    place=[]
    test= True
    re=0

    #les options du doodle sont stockées sous forme de listes (qu'on appelle temps ici) pour la clé "options" du dictionnaire l
    try:
        t=l['closed']
        for temps in l["options"]:

            try:
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
                preferences.append(1)
                place.append(re)
            except:
                almp=1
                preferences.append(0)

            print(preferences[re])
            re+=1


    except:
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
            preferences.append(0)
            place.append(re)
            re+=1




    titre = l["title"]
    lieu = l["location"]["name"]
    description = l["description"]




    now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indique le temps UTC

    #Nous récupérons les évènements du calendrier sur les créneaux donnés par le Doodle
    i = 1
    eventdate=[]
    for option in liste_options :

        if i%2==1 :
            debut=str(option)[0:10]+'T'+str(option)[11:20]+'+01:00'
            i+=1

        else :
            fin=str(option)[0:10]+'T'+str(option)[11:20]+'+01:00'
            events_result = service.events().list(calendarId='primary', timeMin=debut, timeMax=fin).execute()
            events = events_result.get('items', [])


            #Si il n'y a pas d'évènement dans le calendrier à ce créneau, on remplit le doodle puis on remplit le calendrier en réservant le créneau
            if not events:
                eventdate.append(debut)
                eventdate.append(fin)
                preferences[place[i//2-1]]=1


            i+=1
            eventdate2=conversion(eventdate,titre,lieu,description)
    return eventdate2,preferences,optionsHash



def reservecreneaux(eventdate, key):

    fichier=open(key+".txt","w")

    eventtest=[]
    eventfinal=[]
    for k in eventdate:


        service.events().insert(calendarId='primary', body=k).execute()
        event=service.events().list(calendarId='primary', timeMin=k['start']['dateTime'], timeMax=k['end']['dateTime']).execute()['items']
        j=0
        while event[j]['end']['dateTime']!=k['end']['dateTime'] and event[j]['start']['dateTime']!=k['start']['dateTime']:
            j=j+1
        eventfinal.append(event[j])
        fichier.write(str(event[j])+'\n')




    fichier.close()




def efface(key):
    f=open(key + ".txt" , "r")
    for line in f:
        try:
            service.events().delete(calendarId='primary', eventId=eval(line)['id']).execute()
        except:
            print('Déja sup')
    f.close()







def misajour(url,key,nom_utilisateur):


    efface(key)
    eventts=recupcreneaux(url, key)
    reservecreneaux(eventts[0],key)
    preferences = eventts[1]
    participantKey = "et5qinsv"
    optionsHash = eventts[2]

    l=rq.get('https://doodle.com/api/v2.0/polls/dzvsdpkhe534rivt')
    ri=json.loads(l.content)
    li=0
    while(ri['participants'][li]['name']!=nom_utilisateur):
        li+=1

    envoi = {"id":ri['participants'][li]['id'],"name" : nom_utilisateur,
             "optionsHash" : optionsHash, "participantKey": participantKey,
             "preferences" : preferences}
    print(ri['participants'][li]['id'])

    url2=url+"/participants/"+str(ri['participants'][li]['id'])
    ra = rq.put(url2, json = envoi)
    print("Sondage"+key+"mis à jour")






def main():
    #url du sondage
    url = "https://doodle.com/api/v2.0/polls/"
    nom_utilisateur =str(input("Entrer votre nom d'utilisateur \n"))
    mdp=str(input("entrer votre mdp \n"))

    fi=open(nom_utilisateur+mdp+".txt","r")
    print("compte déja existant")
    for ligne in fi:
        url+=ligne
        misajour(url,str(ligne),nom_utilisateur)
    fi.close()




    print("voulez vous ajouter un sondage? o/n")
    rep=str(input())
    if(rep=="o"):
        fi=open(nom_utilisateur+mdp+'.txt',"a")
        key=str(input("Entrez la key du sondage \n"))
        fi.write(key+" \n")
        fi.close()


        #url du sondage
        url = "https://doodle.com/api/v2.0/polls/" + key
        eventts=recupcreneaux(url,key)
        reservecreneaux(eventts[0],key)

        preferences = eventts[1]
        participantKey = "et5qinsv"
        optionsHash =eventts[2]

        envoi = {"name" : nom_utilisateur, "preferences" :
        preferences, "participantKey" : participantKey,
        "optionsHash" : optionsHash}


        url2=url+"/participants"
        ri = rq.post(url2, json = envoi)
        print(ri.text)




"""    try:

        f=open(key+".txt","r")
        print("b")
        f.close()

        misajour(url,key,nom_utilisateur)


    except:
        eventts=recupcreneaux(url,key)
        reservecreneaux(eventts[0],key)

        preferences = eventts[1]
        participantKey = "et5qinsv"
        optionsHash =eventts[2]

        envoi = {"name" : nom_utilisateur, "preferences" :
        preferences, "participantKey" : participantKey,
        "optionsHash" : optionsHash}


        url2=url+"/participants"
        ri = rq.post(url2, json = envoi)
        print(ri.text)"""
