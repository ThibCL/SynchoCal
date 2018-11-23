import os

from flask import Flask
from . import db
from . import auth
from . import page_principale
from . import page_accueil

def create_app(test_config=None):

    #Créé et configure l'application
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(auth.bp)
    app.register_blueprint(page_principale.bp)
    app.add_url_rule('/', endpoint='page_principale')
    app.register_blueprint(page_accueil.bp)
    return app