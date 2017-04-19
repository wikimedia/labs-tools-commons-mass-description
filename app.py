# -*- coding: utf-8 -*-
#
# This file is part of the Tool Labs Flask + OAuth WSGI tutorial
#
# Copyright (C) 2017 Bryan Davis and contributors
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
import mwoauth
import os
import yaml
import simplejson as json
import requests
from urllib.parse import quote


app = flask.Flask(__name__)


# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))


@app.route('/')
def index():
	username = flask.session.get('username', None)
	urlImages = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle=Category%3AMedia_lacking_a_description&cmprop=title&cmtype=file&cmlimit=10'
	r = requests.get(urlImages)
	dataOrig = json.loads(r.text)
	data = dataOrig['query']['categorymembers']
	images = []
	for image in data:
		urlToAsk = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url&titles=' + quote(image['title'])
		response = requests.get(urlToAsk)
		imageDataOrig = json.loads(response.text)
		imageData = imageDataOrig['query']['pages']
		url = imageData[list(imageData.keys())[0]]['imageinfo'][0]['url']
		images.append(url)
	return flask.render_template('index.html', username=username, images=images)


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

    consumer_token = mwoauth.ConsumerToken(
        app.config['CONSUMER_KEY'], app.config['CONSUMER_SECRET'])

    try:
        access_token = mwoauth.complete(
            app.config['OAUTH_MWURI'],
            consumer_token,
            mwoauth.RequestToken(**flask.session['request_token']),
            flask.request.query_string)

        identity = mwoauth.identify(
            app.config['OAUTH_MWURI'], consumer_token, access_token)	
    except Exception:
        app.logger.exception('OAuth authentication failed')
	
    else:
        flask.session['access_token'] = dict(zip(
            access_token._fields, access_token))
        flask.session['username'] = identity['username']

    return flask.redirect(flask.url_for('index'))


@app.route('/logout')
def logout():
    """Log the user out by clearing their session."""
    flask.session.clear()
    return flask.redirect(flask.url_for('index'))

@app.route('/images')
def images():
	urlImages = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&list=categorymembers&cmtitle=Category%3AMedia_lacking_a_description&cmprop=title&cmtype=file&cmlimit=10'
	r = requests.get(urlImages)
	dataOrig = json.loads(r.text)
	data = dataOrig['query']['categorymembers']

	res = []
	for image in data:
		imageRes = {}
		imageRes['title'] = image['title'].replace('File:', '')
		urlToAsk = 'https://commons.wikimedia.org/w/api.php?action=query&format=json&prop=imageinfo&iiprop=url&titles=' + quote(image['title'])
		response = requests.get(urlToAsk)
		imageDataOrig = json.loads(response.text)
		imageData = imageDataOrig['query']['pages']
		imageRes['url'] = imageData[list(imageData.keys())[0]]['imageinfo'][0]['url']
		res.append(imageRes)

	return json.dumps(res)
