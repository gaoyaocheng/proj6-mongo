"""
Flask web app connects to Mongo database.
Keep a simple list of dated memoranda.

Representation conventions for dates:
   - We use Arrow objects when we want to manipulate dates, but for all
     storage in database, in session or g objects, or anything else that
     needs a text representation, we use ISO date strings.  These sort in the
     order as arrow date objects, and they are easy to convert to and from
     arrow date objects.  (For display on screen, we use the 'humanize' filter
     below.) A time zone offset will
   - User input/output is in local (to the server) time.
"""

import flask
from flask import g
from flask import render_template
from flask import request
from flask import url_for
from flask import jsonify

import json
import logging

import arrow
from dateutil import tz

import pymongo
from pymongo import MongoClient
import secrets.admin_secrets
import secrets.client_secrets
MONGO_CLIENT_URL = "mongodb://{}:{}@localhost:{}/{}".format(
    secrets.client_secrets.db_user,
    secrets.client_secrets.db_user_pw,
    secrets.admin_secrets.port,
    secrets.client_secrets.db)

g_uniqid = 0
import CONFIG
app = flask.Flask(__name__)
app.secret_key = CONFIG.secret_key


try:
    dbclient = MongoClient(MONGO_CLIENT_URL)
    db = getattr(dbclient, secrets.client_secrets.db)
    collection = db.dated

except:
    print("Failure opening database.  Is Mongo running? Correct password?")
    sys.exit(1)

@app.route("/")
@app.route("/index")
def index():
  g.memos = get_memos()
  flask.session['memos'] = g.memos
  return flask.render_template('index.html')


@app.route("/new")
def new():
  flask.session['record'] = {}
  flask.session['record']['type'] = "dated_memo"
  return flask.render_template('new.html')

@app.route("/_datetime")
def datetime():
  data = request.args.get('time', 0, type=str).strip()
  mdata = arrow.get(data,"MM/DD/YYYY").naive
  flask.session['record']['date'] = mdata
  return jsonify(result=True)

@app.route("/_memocontext")
def memocontext():
  data = request.args.get('context', 0, type=str).strip()
  flask.session['record']['text'] = data
  return jsonify(result=True)

@app.route("/_save")
def save():
  if 'record' not in flask.session.keys():
    return jsonify(result=False)
  if 'date' not in flask.session['record'] or 'text' not in flask.session['record']:
    return jsonify(result=False)
  global g_uniqid
  flask.session['record']['id'] = g_uniqid
  g_uniqid += 1
  collection.insert(flask.session['record'])
  del flask.session['record']
  return jsonify(result=True)

@app.route("/_cancel")
def cancel():
  return jsonify(result=True)

@app.route("/_choose")
def choose():
  check = request.args.get('che', 0, type=str)
  index = request.args.get('idx', 0, type=int)
  if check == "true":
    flask.session['memos'][index - 1]['delete'] = True
  else:
    flask.session['memos'][index - 1]['delete'] = False


  return jsonify(result=True)

@app.route("/_delete")
def delete():
  for record in flask.session['memos']:
    if record['delete']:
      collection.remove({'id':record['id']})

  return jsonify(result=True)
@app.errorhandler(404)
def page_not_found(error):
    return flask.render_template('page_not_found.html',
                                 badurl=request.base_url,
                                 linkback=url_for("index")), 404



@app.template_filter( 'humanize' )
def humanize_arrow_date( date ):
    try:
        then = arrow.get(date).to('local')
        now = arrow.utcnow().to('local')
        if then.date() == now.date():
            human = "Today"
        else:
            human = then.humanize(now)
            if "hours" in human or "in a day" in human:
                human = "Tomorrow"
            elif "a day ago" == human:
                human = "Yesterday"
    except:
        human = date
    return human


def get_memos():
    records = [ ]
    for record in collection.find( { "type": "dated_memo" } ).sort('date', pymongo.ASCENDING):
        record['date'] = arrow.get(record['date']).isoformat()
        record['delete'] = False
        del record['_id']
        records.append(record)
    return records


if __name__ == "__main__":
    app.debug=CONFIG.DEBUG
    app.logger.setLevel(logging.DEBUG)
    app.run(port=CONFIG.PORT,host="0.0.0.0")


