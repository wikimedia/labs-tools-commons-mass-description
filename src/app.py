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
from flask import redirect, request, jsonify, make_response
import mwoauth
import mwparserfromhell
from requests_oauthlib import OAuth1

app = flask.Flask(__name__)
application = app


# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

key = app.config['CONSUMER_KEY']
secret = app.config['CONSUMER_SECRET']

@app.before_request
def force_https():
    if request.headers.get('X-Forwarded-Proto') == 'http':
        return redirect(
            'https://' + request.headers['Host'] + request.headers['X-Original-URI'],
            code=301
        )
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE')
    return response

@app.route('/')
def index():
	username = flask.session.get('username')
	if username is not None:
		if blocked()['blockstatus']:
			return flask.render_template('blocked.html')
		else:
			return flask.render_template('tool.html')
	else:
		return flask.render_template('login.html')

@app.route('/api-username')
def username():
	data = {'username': flask.session.get('username')}
	return jsonify(data)

def langs():
	params = {
		"action": "sitematrix",
		"format": "json",
		"smtype": "language",
		"smstate": "all",
		"smlangprop": "code|name",
		"smlimit": "max"
	}
	r = requests.get(app.config['API_MWURI'], params=params)
	data = r.json()
	langs = []
	for key in data['sitematrix'].keys():
		if key != 'count':
			langs.append({
				'code': data['sitematrix'][key]['code'],
				'name': data['sitematrix'][key]['name']
			})
	res = {
		'status': 'ok',
		'langs': langs
	}
	return res

def thumburl(url, size):
	return url.replace('commons', 'commons/thumb') + '/' + str(size) + 'px-' + url.split('/')[-1] + '.png'

@app.route('/api-blocked')
def apiblocked():
	return jsonify(blocked())

def blocked():
	username = flask.session.get('username')
	if username == None:
		response = {
			'status': 'error',
			'errorcode': 'anonymoususe'
		}
		return response
	payload = {
		"action": "query",
		"format": "json",
		"list": "users",
		"usprop": "blockinfo",
		"ususers": username
	}
	r = requests.get(app.config['API_MWURI'], params=payload)
	data = r.json()['query']['users'][0]
	response = {
		'status': 'ok',
		'blockstatus': 'blockid' in data
	}
	if response['blockstatus']:
		response['blockdata'] = {
			'blockedby': data['blockedby'],
			'blockexpiry': data['blockexpiry'],
			'blockreason': data['blockreason']
		}
	return response

@app.route('/api-described')
def apidescribed():
	title = request.args.get('title')
	if title == None:
		return 'bad request'
	return {
		'described': described(title)
	}

def described(page):
	payload = {
		"action": "query",
		"format": "json",
		"prop": "revisions",
		"titles": page,
		"rvprop": "content",
		"rvlimit": "1"
	}
	r = requests.get(
		app.config['API_MWURI'],
		params=payload
	)
	data = r.json()
	pageid = list(data['query']['pages'].keys())[0]
	if pageid == '-1':
		return {
			'status': 'error',
			'errorcode': 'nonexistentpage'
		}
	pagecontent = data['query']['pages'][pageid]['revisions'][0]['*']
	code = mwparserfromhell.parse(pagecontent)
	for template in code.filter_templates():
		if template.name.strip() == 'Information':
			for param in template.params:
				if param.name.strip() == 'description':
					if param.value.strip() != '':
						return True
					return False

@app.route('/api-images')
def images():
	paginateby = 10
	offsetsrc = request.args.get('offset')
	if offsetsrc == None:
		offset = 0
	else:
		offset = int(offsetsrc)
	limit = paginateby*(offset+1)
	categorysrc = request.args.get('category')
	if categorysrc == None:
		category = "Category:Media_lacking_a_description"
	else:
		category = categorysrc
	params = {
		"action": "query",
		"format": "json",
		"prop": "imageinfo",
		"generator": "categorymembers",
		"iiprop": "url",
		"gcmtitle": category.replace(' ', '_'),
		"gcmtype": "file",
		"gcmlimit": limit
	}
	r = requests.get(app.config['API_MWURI'], params=params)
	data = r.json()
	res = {
		'images': [],
		'status': 'ok'
	}
	images = []
	for page in data['query']['pages']:
		imagedata = data['query']['pages'][page]
		if category == "Category:Media_lacking_a_description" or described(imagedata['title']) == False:
			newimagedata = {
				'title': imagedata['title'],
				'id': imagedata['pageid'],
				'url': imagedata['imageinfo'][0]['url'],
				'thumburl': thumburl(imagedata['imageinfo'][0]['url'], 100)
			}
			images.append(newimagedata)
	res['images'] = images[-10:]
	return jsonify(res)

@app.route('/api-edit', methods=['post'])
def editall():
	data = request.get_json()
	languages = langs()['langs']
	langcodes = []
	for item in languages:
		langcodes.append(item['code'])
	for image in data:
		if 'description' not in image or 'lang' not in image or 'id' not in image:
			if 'id' in image:
				id = image['id']
			else:
				id = 'n-a'
			response = {
				'status': 'error',
				'errorcode': 'mustpassparams',
				'id': id
			}
			return make_response(jsonify(response), 400)
		if image['lang'] not in langcodes:
			response = {
				'status': 'error',
				'errorcode': 'nonexistentlang',
				'id': image['id']
			}
			return make_response(jsonify(response), 400)
		#image['id'] = '57297576' # Just for debugging; User:Martin Urbanec/sand
		imageres = edit(str(image['id']), image['description'], image['lang'])
		if imageres['status'] != 'ok':
			response = {
				'status': 'error',
				'errorcode': imageres['errorcode'],
				'id': image['id']
			}
			return make_response(jsonify(response), 400)
	response = {'status': 'ok'}
	return jsonify(response)

def edit(id, description, lang):
	request_token_secret = flask.session.get('request_token_secret', None)
	request_token_key = flask.session.get('request_token_key', None)
	auth = OAuth1(key, secret, request_token_key, request_token_secret)
	payload = {
		"action": "query",
		"format": "json",
		"prop": "revisions",
		"pageids": id,
		"rvprop": "content",
		"rvlimit": "1"
	}
	r = requests.get(
		app.config['API_MWURI'],
		params=payload,
		auth=auth
	)
	data = r.json()
	pageid = list(data['query']['pages'].keys())[0]
	if pageid == '-1':
		return {
			'status': 'error',
			'errorcode': 'nonexistentpage'
		}
	pagecontent = data['query']['pages'][pageid]['revisions'][0]['*']
	code = mwparserfromhell.parse(pagecontent)
	for template in code.filter_templates():
		if template.name.strip() == 'Information' or template.name.strip() == 'information':
			for param in template.params:
				if param.name.strip() == 'description' or param.name.strip() == 'Description':
					if param.value.strip() != '':
						return {
							'status': 'error',
							'errorcode': 'alreadydescribed'
						}
					param.value = '{{' + lang + '|1=' + description + '}}' + '\n'
					break
			break
	payload = {
		"action": "query",
		"format": "json",
		"meta": "tokens",
		"type": "csrf"
	}
	r = requests.get(
		app.config['API_MWURI'],
		params=payload,
		auth=auth
	)
	token = r.json()['query']['tokens']['csrftoken']
	payload = {
		"action": "edit",
		"format": "json",
		"pageid": id,
		"text": str(code),
		"summary": "Added description with Commons mass description tool",
		"token": token
	}
	r = requests.post(
		app.config['API_MWURI'],
		data=payload,
		auth=auth
	)
	data = r.json()
	if 'edit' in data:
		return {
			'status': 'ok',
			'reply': data
		}
	else:
		if data['error']['code'] == 'blocked':
			errorcode = 'blocked'
		elif data['error']['code'] == 'protectedpage':
			errorcode = 'protectedpage'
		else:
			errorcode = 'unknown'
		return {
			'status': 'error',
			'errorcode': errorcode
		}

@app.route('/api-langs')
def apilangs():
	return jsonify(langs())

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
