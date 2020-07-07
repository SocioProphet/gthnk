import re
import os
import flask
import datetime

from sqlalchemy import desc
from flask_login import login_required
from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField, validators

from ..models.entry import Entry
from ..librarian import Librarian

root = flask.Blueprint('gthnk', __name__)

class NoteForm(FlaskForm):
    entry = TextAreaField('Entry',
        validators=[validators.DataRequired()],
        render_kw={
            'class': 'form-control rounded-0',
            'rows': 10
        }
    )
    save_button = SubmitField("Save")

@root.route('/note', methods=['GET', 'POST'])
@login_required
def note_view():
    form = NoteForm()
    datestamp = datetime.datetime.today().strftime('%Y-%m-%d')
    timestamp = datetime.datetime.today().strftime('%H%M')

    if form.validate_on_submit():
        entry = form.entry.data

        buf = ""

        # if web journal file size is 0, write the date first
        size_bytes = 0
        if os.path.isfile(flask.current_app.config["WEB_JOURNAL_FILE"]):
            size_bytes = os.path.getsize(flask.current_app.config["WEB_JOURNAL_FILE"])
        if size_bytes == 0:
            buf += "{}\n".format(datestamp)

        # then write the time marker
        buf += "\n{}\n\n".format(timestamp)
        buf += entry + "\n"

        with open(flask.current_app.config["WEB_JOURNAL_FILE"], 'a') as f:
            f.write(buf)
        
        return flask.redirect(flask.url_for('day.buffer_view'))
    else:
        return flask.render_template('note-view.html.j2',
            form=form,
            timestamp=timestamp,
            datestamp=datestamp
        )


@root.route("/search")
@login_required
def search_view():
    if not flask.request.args:
        return flask.redirect(flask.url_for("gthnk.index"))
    else:
        query_str = flask.request.args['q']
        query = Entry.query.filter(
            Entry.content.contains(query_str)).order_by(desc(Entry.timestamp))
        results = query.all()[:20]

        for idx in range(0, len(results)):
            results[idx].content = re.sub(query_str, "**{}**".format(
                query_str), results[idx].content, flags=re.I)

        return flask.render_template('results-list.html.j2',
            data=results,
            query_str=query_str,
            count=query.count()
            )

@root.route("/refresh")
@login_required
def refresh():
    librarian = Librarian(flask.current_app)
    librarian.rotate_buffers()
    return flask.redirect(flask.url_for('day.latest_view'))

###
# Index

@root.route('/')
def index():
    return flask.render_template('index.html.j2')
