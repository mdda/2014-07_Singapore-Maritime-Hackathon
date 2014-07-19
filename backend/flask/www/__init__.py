from flask import Flask, request, Response, render_template, session
from werkzeug import ImmutableDict

import os # environ
import flask

app = Flask(__name__)
app.jinja_env.add_extension('pyjade.ext.jinja.PyJadeExtension')

app.secret_key = 'ENTER RANDOM STUFF HERE'
app.debug=True # Works in uwsgi environment

#import platform
#hostname = platform.uname()[1]

# See http://docs.sqlalchemy.org/ru/latest/dialects/sqlite.html#connect-strings
app.config['DATABASE'] = os.environ.get("FLASK_DB", 'sqlite:///sqlite_hackathon.db') # Relative URL
app.config['SENDMAIL'] = os.environ.get("FLASK_MAIL", False)
app.config['SENDMAIL_FILE'] = os.environ.get("FLASK_MAIL_FILE", 'mime_message.txt')
app.debug = os.environ.get("FLASK_DEBUG", False)

#if hostname == 'example.com':
#    #app.config['DATABASE'] = 'sqlite:////home/USERNAME/hackathon-starter-flask-plus/backend/flask/sqlite_hackathon.db' # Absolute URL
#    app.config['SENDMAIL'] = True
#    # app.debug=False  # This appears to be safe under uwsgi - 

#app.config['DATABASE'] = os.environ.get('FLASK_OVERRIDE_DB', app.config['DATABASE'])

# Pull in routes
import www.main
import www.auth
import www.admin

import www.database as db

@app.teardown_request
def shutdown_session(exception=None):
    db.session.remove()

@app.after_request
def after_request(response):
    db.session.commit()
    db.session.remove()
    return response

