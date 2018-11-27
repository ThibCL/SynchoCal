from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort

from applicationCode.auth import login_required
from applicationCode.db import get_db
from . import with_doodle

bp = Blueprint('page_principale', __name__)

@bp.route('/')
def liste_sondages():
    db = get_db()
    sondages = db.execute(
        'SELECT * FROM sondage JOIN (SELECT su.sondage_key AS s_key FROM user JOIN sondage_user su ON user.id=su.user_id) sond ON sondage.key=sond.s_key'
    ).fetchall()
    return render_template('liste_sondages.html', sondages=sondages)

@bp.route('/ajouter', methods=('GET', 'POST'))
@login_required
def ajouter():
    error = None
    if request.method == 'POST':
        key = request.form['key']

        if not key:
            error = 'Veuillez entrer la clé du sondage.'

        if error is not None:
            flash(error)
        else:
            sond = with_doodle.recup_creneau(key)
            #db = get_db()
            #db.execute(
            #    'INSERT INTO sondage (title, body, author_id)'
            #    ' VALUES (?, ?, ?)',
            #    (title, body, g.user['id'])
            #)
            #db.commit()
            print(sond)
            return redirect(url_for('blog.index'))

    return render_template('ajouter.html')
