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
from flask import Response
import mwoauth
import mwoauth.flask
from requests_oauthlib import OAuth1
from flask_mwoauth import MWOAuth
from flask import request
import mwparserfromhell

app = flask.Flask(__name__)


# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

key = app.config['CONSUMER_KEY']
secret = app.config['CONSUMER_SECRET']

@app.route('/')
def index():
    username = flask.session.get('username', None)
    return flask.render_template(
        'index.html', username=username)


@app.route('/images')
def images():
	toFetch = 10
	offset = 0
	if request.args.get('offset') == None:
		offset = 0
	else:
		offset = int(request.args.get('offset'))
	if offset < 0:
		offset = 0
	toFetch += offset
	urlImages = app.config['API_MWURI'] + '?action=query&format=json&list=categorymembers&cmtitle=Category%3AMedia_lacking_a_description&cmprop=title&cmtype=file&cmlimit=' + str(toFetch)
	r = requests.get(urlImages)
	dataOrig = json.loads(r.text)
	data = dataOrig['query']['categorymembers']

	res = []
	for image in data:
		imageRes = {}
		imageRes['title'] = image['title'].replace('File:', '')
		urlToAsk = app.config['API_MWURI'] + '?action=query&format=json&prop=imageinfo&iiprop=url&titles=' + quote(image['title'])
		response = requests.get(urlToAsk)
		imageDataOrig = json.loads(response.text)
		imageData = imageDataOrig['query']['pages']
		imageRes['url'] = imageData[list(imageData.keys())[0]]['imageinfo'][0]['url']
		res.append(imageRes)
	res = res[-10:]
	return Response(json.dumps(res), mimetype='application/json')

@app.route('/edit')
def edit():
	request_token_secret = flask.session.get('request_token_secret', None)
	request_token_key = flask.session.get('request_token_key', None)
	auth = OAuth1(key, secret, request_token_key, request_token_secret)
	r = requests.post(url=app.config['API_MWURI'], params={'format': 'json', 'action': 'query', 'meta': 'tokens', 'type': 'csrf'}, headers={'User-Agent': 'Commons Mass Description filler'}, auth=auth)
	token = json.loads(r.content)['query']['tokens']['csrftoken']
	"""
	payload = {'format': 'json', 'action': 'edit', 'title': 'User:Martin Urbanec/sand', 'section': 'new', 'sectiontitle': 'Test', 'text': 'This is message posted using entriely new tool!', 'summary': '/* Test */ Hello', 'watchlist': 'nochange', 'token': token}
	r = requests.post(url=app.config['API_MWURI'], data=payload, headers={'User-Agent': 'Commons Mass Description filler'}, auth=auth)
	return r.content
	"""
	description = request.args.get('description')
	image = request.args.get('image')
	if description == None or image == None:
		reply = {'status': 'error', 'data': {'errorcode': 'mustpassparams', 'description': 'You must pass both "description" and "image" GET params'}}
		return Response(json.dumps(reply), mimetype='application/json')
	data = {'action': 'query', 'prop': 'revisions', 'rvprop': 'content', 'format': 'json', 'titles': image}
	r = requests.post(url=app.config['API_MWURI'], params=data)
	data = json.loads(r.content)['query']['pages']
	text = data[str(list(data.keys())[0])]['revisions'][0]['*']
	code = mwparserfromhell.parse(text)

	for template in code.filter_templates():
		if template.name.matches('Information'):
			if template.has('description'):
				template.remove('description')
			template.add('description', description)

	text = str(code)
	return text

@app.route('/login')
def login():
    """Initiate an OAuth login.

    Call the MediaWiki server to get request secrets and then redirect the
    user to the MediaWiki server to sign the request.
    """
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
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))


if __name__ == "__main__":
	app.run(debug=True, threaded=True)
