# -*- coding: utf-8 -*-
#
# This program is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
# more details.
#
# You should have received a copy of the GNU General Public License along
# with this program.  If not, see <http://www.gnu.org/licenses/>.

import flask
import os
import yaml
import simplejson as json
import requests
from urllib.parse import quote
from flask import Response, make_response
import mwoauth
import mwoauth.flask
from requests_oauthlib import OAuth1
from flask_mwoauth import MWOAuth
from flask import request
import mwparserfromhell

app = flask.Flask(__name__)
application = app


# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

key = app.config['CONSUMER_KEY']
secret = app.config['CONSUMER_SECRET']

@app.route('/')
def index():
	if request.headers['X-Forwarded-Proto'] == "http":
		return flask.redirect(request.url.replace('http://', 'https://')) # Force HTTPS for our users
	username = flask.session.get('username', None)
	return flask.render_template('index.html', username=username)


@app.route('/images')
def images():
	if request.headers['X-Forwarded-Proto'] == "http":
		return flask.redirect(request.url.replace('http://', 'https://')) # Force HTTPS for our users
	toFetch = 10
	if request.args.get('toFetch') == None:
		toFetch = 10
	else:
		offset = int(request.args.get('toFetch'))
	if toFetch < 1:
		toFetch = 10
	offset = 0
	if request.args.get('offset') == None:
		offset = 0
	else:
		offset = int(request.args.get('offset'))
	if offset < 0:
		offset = 0
	toFetch += offset
	payload = {'action': 'query', 'format': 'json', 'list': 'categorymembers', 'cmtitle': 'Category:Media_lacking_a_description', 'cmprop': 'title', 'cmtype': 'file', 'cmlimit': str(toFetch)}
	r = requests.post(url=app.config['API_MWURI'], params=payload)
	dataOrig = json.loads(r.content)
	data = dataOrig['query']['categorymembers']

	filenames = []
	i = 0
	for image in data:
		filenames.append(image['title'])

	filenames = filenames[-10:]

	payload = {'action': 'query', 'format': 'json', 'prop': 'imageinfo', 'iiprop': 'url', 'titles': "|".join(filenames)}
	r = requests.get(url=app.config['API_MWURI'], params=payload)
	data = json.loads(r.content)
	data = data["query"]["pages"]

	res = []
	for image in data:
		imageRes = {}
		imageRes['title'] = data[image]["title"].replace("\n", "")
		imageRes["url"] = data[image]["imageinfo"][0]["url"]
		res.append(imageRes)

	r = Response(json.dumps(res), mimetype='application/json')
	r.headers.set('Access-Control-Allow-Origin', '*')
	return r

@app.route('/edit')
def edit():
	if request.headers['X-Forwarded-Proto'] == "http":
		return flask.redirect(request.url.replace('http://', 'https://')) # Force HTTPS for our users
	request_token_secret = flask.session.get('request_token_secret', None)
	request_token_key = flask.session.get('request_token_key', None)
	auth = OAuth1(key, secret, request_token_key, request_token_secret)
	description = request.args.get('description')
	image = request.args.get('image')
	lang = request.args.get('lang')

	if description == None or image == None:
		reply = {'status': 'error', 'data': {'errorcode': 'mustpassparams', 'description': 'You must pass both "description" and "image" GET params'}}
		r = Response(json.dumps(reply), mimetype='application/json')
		r.headers.set('Access-Control-Allow-Origin', '*')
		return r

	if lang != None:
		if checkLang(lang):
			description = '{{' + lang + '|' + description + '}}'
		else:
			reply = {'status': 'error', 'data': {'errorcode': 'nonexistentlang', 'description': 'You can\'t pass nonexistent language code. Won\'t process.'}}
			r = Response(json.dumps(reply), mimetype='application/json')
			r.headers.set('Access-Control-Allow-Origin', '*')
			return r

	data = {'action': 'query', 'prop': 'revisions', 'rvprop': 'content', 'format': 'json', 'titles': image}
	r = requests.post(url=app.config['API_MWURI'], params=data)
	data = json.loads(r.content)['query']['pages']
	pageid = list(data.keys())[0]
	if pageid == "-1":
		reply = {'status': 'error', 'data': {'errorcode': 'nonexistentimg', 'description': 'The image you are trying to edit doesn\t exist'}}
		r = Response(json.dumps(reply), mimetype='application/json')
		r.headers.set('Access-Control-Allow-Origin', '*')
		return r
	text = data[str(pageid)]['revisions'][0]['*']
	code = mwparserfromhell.parse(text)

	if not checkDescription(code):
		for template in code.filter_templates():
			if template.name.matches('Information') or template.name.matches('information'):
				if template.has("description"):
					template.remove("description")
					template.add("description", description + '\n')
				elif template.has("Description"):
					template.remove("Description")
					template.add("Description", description + '\n')
				else:
					template.add("description", description + '\n')
				break

		r = requests.post(url=app.config['API_MWURI'], params={'format': 'json', 'action': 'query', 'meta': 'tokens', 'type': 'csrf'}, headers={'User-Agent': 'Commons Mass Description filler'}, auth=auth)
		token = json.loads(r.content)['query']['tokens']['csrftoken']

		text = str(code)
		payload = {'format': 'json', 'action': 'edit', 'title': image, 'summary': 'Add description', 'text': text, 'token': token}
		r = requests.post(url=app.config['API_MWURI'], data=payload, headers={'User-Agent': 'Commons Mass Description filler'}, auth=auth)
		data = json.loads(r.content)
		if data['edit']['result'] == 'Success':
			reply = {'status': 'ok', 'data': {}}
			r = Response(json.dumps(reply), mimetype="application/json")
			r.headers.set('Access-Control-Allow-Origin', '*')
			return r
		else:
			reply = {'status': 'error', 'data': {'errorcode': 'mwinternal', 'description': 'There was some internal MediaWiki error. Useful details may be present in API reply from MediaWiki', 'apireply': data}}
			r = Response(json.dumps(reply), mimetype="application/json")
			r.headers.set('Access-Control-Allow-Origin', '*')
			return r
	else:
		reply = {'status': 'error', 'data': {'errorcode': 'descriptionalreadypresent', 'description': 'Description of the image was already present. Skipping. '}}
		r = Response(json.dumps(reply), mimetype="application/json")
		r.headers.set('Access-Control-Allow-Origin', '*')
		return r


def checkDescription(code):
	for template in code.filter_templates():
		if template.name.matches('Information') or template.name.matches('information'):
			if not(template.has('description') or template.has('Description')):
				return False
			else:
				if template.has('description'):
					if template.get('description').value == '' or template.get('description').value == '\n':
						return False
					else:
						return True
				elif template.has('Description'):
					if template.get('Description').value == '' or template.get('Description').value == '\n':
						return False
					else:
						return True
				else:
					return False
			break
	return False

@app.route('/description')
def checkDescriptionPage():
	if request.headers['X-Forwarded-Proto'] == "http":
		return flask.redirect(request.url.replace('http://', 'https://')) # Force HTTPS for our users
	image = request.args.get('image')
	data = {'action': 'query', 'prop': 'revisions', 'rvprop': 'content', 'format': 'json', 'titles': image}
	r = requests.post(url=app.config['API_MWURI'], params=data)
	data = json.loads(r.content)['query']['pages']
	text = data[str(list(data.keys())[0])]['revisions'][0]['*']
	code = mwparserfromhell.parse(text)

	reply = {'description': checkDescription(code)}

	r = Response(json.dumps(reply), mimetype="application/json")
	r.headers.set('Access-Control-Allow-Origin', '*')
	return r

def checkLang(lang):
	pagetocheck = 'Template:' + lang.lower()
	data = {'action': 'query', 'format': 'json', 'titles': pagetocheck}
	r = requests.post(url=app.config['API_MWURI'], params=data)
	d = json.loads(r.content)
	if list(d['query']['pages'].keys())[0] == '-1':
		return False
	return True

@app.route('/checkLang')
def checkLangPage():
	res = checkLang(request.args.get('lang'))
	reply = {'langexist': res}
	r = Response(json.dumps(reply), mimetype="application/json")
	r.headers.set('Access-Control-Allow-Origin', '*')
	return r

@app.route('/login')
def login():
	"""Initiate an OAuth login.
	Call the MediaWiki server to get request secrets and then redirect the
	user to the MediaWiki server to sign the request.
	"""
	if request.headers['X-Forwarded-Proto'] == "http":
		return flask.redirect(request.url.replace('http://', 'https://')) # Force HTTPS for our users
	consumer_token = mwoauth.ConsumerToken(
		app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])
	try:
		redirect, request_token = mwoauth.initiate(
		app.config['OAUTH_MWURI'], consumer_token)
	except Exception:
		app.logger.exception('mwoauth.initiate failed')
		return flask.redirect(flask.url_for('index'))
	else:
		flask.session['request_token'] = dict(zip(
		request_token._fields, request_token))
		return flask.redirect(redirect)


@app.route('/oauth-callback')
def oauth_callback():
	"""OAuth handshake callback."""
	if request.headers['X-Forwarded-Proto'] == "http":
		return flask.redirect(request.url.replace('http://', 'https://')) # Force HTTPS for our users
	if 'request_token' not in flask.session:
		flask.flash(u'OAuth callback failed. Are cookies disabled?')
		return flask.redirect(flask.url_for('index'))
	consumer_token = mwoauth.ConsumerToken(app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

	try:
		access_token = mwoauth.complete(
		app.config['OAUTH_MWURI'],
		consumer_token,
		mwoauth.RequestToken(**flask.session['request_token']),
		flask.request.query_string)
		identity = mwoauth.identify(app.config['OAUTH_MWURI'], consumer_token, access_token)
	except Exception:
		app.logger.exception('OAuth authentication failed')
	else:
		flask.session['request_token_secret'] = dict(zip(access_token._fields, access_token))['secret']
		flask.session['request_token_key'] = dict(zip(access_token._fields, access_token))['key']
		flask.session['username'] = identity['username']

	return flask.redirect(flask.url_for('index'))


@app.route('/logout')
def logout():
	"""Log the user out by clearing their session."""
	if request.headers['X-Forwarded-Proto'] == "http":
		return flask.redirect(request.url.replace('http://', 'https://')) # Force HTTPS for our users
	flask.session.clear()
	return flask.redirect(flask.url_for('index'))

@app.route('/proto')
def proto():
	if request.headers['X-Forwarded-Proto'] == "http":
		return flask.redirect(request.url.replace('http://', 'https://')) # Force HTTPS for our users
	return "2"

if __name__ == "__main__":
	app.run(debug=True, threaded=True)
