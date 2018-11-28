Pour faire fonctionner l'application WEB :

1) Telecharger Python 3.7

2) Installer Flask : pip install Flask

3) A chaque nouvelle utilisation, dans l'invite de commande executer les lignes suivantes :
    set FLASK_APP=applicationCode
    set FLASK_ENV=development

4) Pour la première utilisation seulement, il faut initialiser la base de donnée :
    py -m flask init-db

5) Pour pouvoir utiliser l'application, placer le fichier credentials.json dans le même dossier que l'application (dans le dossier applicationCode)
cf. rapport partie "Connection du calendrier Google à Python via l’API"

6) Pour lancer l'application, se placer dans le répertoire de l'application et executer dans l'invite de commande :
    py -m flask run

7) Pour permettre à l'application de fonctionner, il faut télécharger certains modules :
    pip install --upgrade google-api-python-client oauth2client
    pip install requests
