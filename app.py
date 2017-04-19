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
from flask_mwoauth import MWOAuth

app = flask.Flask(__name__)


# Load configuration from YAML file
__dir__ = os.path.dirname(__file__)
app.config.update(
    yaml.safe_load(open(os.path.join(__dir__, 'config.yaml'))))

key = app.config['CONSUMER_KEY']
secret = app.config['CONSUMER_SECRET']

mwoauth = MWOAuth(consumer_key=key, consumer_secret=secret)
app.register_blueprint(mwoauth.bp)

@app.route('/')
def index():
    username = mwoauth.get_current_user(True)
    return flask.render_template(
        'index.html', username=username)


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
	return Response(json.dumps(res), mimetype='application/json')

@app.route('/edit')
def edit():
	result = request({'action': 'query', 'meta': 'userinfo'}, url='https://commons.wikimedia.org/w/api.php')
	return Response(json.dumps(result), mimetype='application/json')
