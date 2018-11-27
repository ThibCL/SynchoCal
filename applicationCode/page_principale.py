from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from applicationCode.auth import login_required
from applicationCode.db import get_db
from datetime import datetime

bp = Blueprint('page_principale', __name__)

#Cette page est la page principale à laquelle accède l'utilisateur lorsqu'il est connecté

#Elle affiche l'ensemble de ses sondages en cours
@bp.route('/')
@login_required
def liste_sondages():
    db = get_db()
    sondages = db.execute(
        'SELECT * FROM sondage JOIN (SELECT su.sondage_key AS s_key FROM sondage_user su WHERE su.user_id = (?)) sond'
        ' ON sondage.key=sond.s_key', (g.user['id'],)
    ).fetchall()
    return render_template('liste_sondages.html', sondages=sondages)

#(SELECT su.sondage_key AS s_key FROM sondage_user su WHERE su.user_id = ?) sond
#L'utilisateur peut ajouter des sondages à partir de leur clé ("key")
@bp.route('/ajouter', methods=('GET', 'POST'))
@login_required
def ajouter():
    if request.method == 'POST':
        key = request.form['key']
        error = None
        db = get_db()

        if not key:
            error = 'Veuillez entrer la clé du sondage.'

        elif db.execute(
            'SELECT key FROM sondage WHERE key = ?', (key,)
        ).fetchone() is not None:
            error = 'Le sondage dont la clé est {} existe déjà !'.format(key)

        if error is not None:
            flash(error)
        else:
            #sond = with_doodle.recup_creneau(key)
            titre ='Titre du sondage test2'
            date=datetime.now().date()
            lieu = 'Paris'
            description = 'C\'est la description du sondage test1'
            liste_options='Liste des options écrites dans une chaine de caractère test1'
            db.execute(
                'INSERT INTO sondage (key, titre, date_entree, date_maj, lieu, description, liste_options)'
                ' VALUES (?, ?, ?, ?, ?, ?, ?)',
                (key, titre, date, date, lieu, description, liste_options)
            )
            db.execute(
                'INSERT INTO sondage_user (sondage_key, user_id)'
                ' VALUES (?, ?)',
            (key, g.user['id'])
            )
            db.commit()
            return redirect(url_for('page_principale'))

    return render_template('ajouter.html')

#L'utilisateur peut mettre à jour ses sondages afin d'actualiser les changements qu'il y aurait pu avoir, ou de voir si il est final
@bp.route('/<string:key>/mise_a_jour', methods=('POST',))
@login_required
def mise_a_jour(key):
    db = get_db()
    #fonction de mise à jour du sondage
    desc = 'Le sondage a été mis à jour'
    date_maj=datetime.now().date()
    db.execute(
                'UPDATE sondage SET description = ?, date_maj = ?'
                ' WHERE key = ?',
                (desc, date_maj,key)
            )
    db.commit()
    return redirect(url_for('page_principale'))

#L'utilisateur peut supprimer ses sondages si il le souhaite
@bp.route('/<string:key>/supprimer', methods=('POST',))
@login_required
def supprimer(key):
    db = get_db()
    db.execute(
                'DELETE FROM sondage WHERE key = ?',(key,)
            )
    db.commit()
    return redirect(url_for('page_principale'))
