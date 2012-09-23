# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import base64
import os
import os.path
import urllib
import hmac
import json
import hashlib
from base64 import urlsafe_b64decode, urlsafe_b64encode

import requests
from flask import Flask, session, request, redirect, render_template, url_for

FB_APP_ID = os.environ.get('FACEBOOK_APP_ID')
requests = requests.session()

app_url = 'https://graph.facebook.com/{0}'.format(FB_APP_ID)
FB_APP_NAME = json.loads(requests.get(app_url).content).get('name')
FB_APP_SECRET = os.environ.get('FACEBOOK_SECRET')

SECRET_KEY = os.environ.get('SECRET_KEY')


def oauth_login_url(preserve_path=True, next_url=None):
    fb_login_uri = ("https://www.facebook.com/dialog/oauth"
                    "?client_id=%s&redirect_uri=%s" %
                    (app.config['FB_APP_ID'], request.url_root))

    if app.config['FBAPI_SCOPE']:
        fb_login_uri += "&scope=%s" % ",".join(app.config['FBAPI_SCOPE'])
    return fb_login_uri


def simple_dict_serialisation(params):
    return "&".join(map(lambda k: "%s=%s" % (k, params[k]), params.keys()))


def base64_url_encode(data):
    return base64.urlsafe_b64encode(data).rstrip('=')


def fbapi_get_string(path,
    domain=u'graph', params=None, access_token=None,
    encode_func=urllib.urlencode):
    """Make an API call"""

    if not params:
        params = {}
    params[u'method'] = u'GET'
    if access_token:
        params[u'access_token'] = access_token

    for k, v in params.iteritems():
        if hasattr(v, 'encode'):
            params[k] = v.encode('utf-8')

    url = u'https://' + domain + u'.facebook.com' + path
    params_encoded = encode_func(params)
    url = url + params_encoded
    print url
    result = requests.get(url).content

    return result


def fbapi_auth(code):
    params = {'client_id': app.config['FB_APP_ID'],
              'redirect_uri': request.url_root + 'auth/',
              'client_secret': app.config['FB_APP_SECRET'],
              'code': code}

    result = fbapi_get_string(path=u"/oauth/access_token?", params=params,
                              encode_func=simple_dict_serialisation)

    pairs = result.split("&", 1)
    result_dict = {}
    for pair in pairs:
        (key, value) = pair.split("=")
        result_dict[key] = value
    return (result_dict["access_token"], result_dict["expires"])


def fbapi_get_application_access_token(id):
    token = fbapi_get_string(
        path=u"/oauth/access_token",
        params=dict(grant_type=u'client_credentials', client_id=id,
                    client_secret=app.config['FB_APP_SECRET']),
        domain=u'graph')

    token = token.split('=')[-1]
    if not str(id) in token:
        print 'Token mismatch: %s not in %s' % (id, token)
    return token


def fql(fql, token, args=None):
    if not args:
        args = {}

    args["query"], args["format"], args["access_token"] = fql, "json", token

    url = "https://api.facebook.com/method/fql.query"

    r = requests.get(url, params=args)
    return json.loads(r.content)


def fb_call(call, args=None):
    url = "https://graph.facebook.com/{0}".format(call)
    r = requests.get(url, params=args)
    # print r.url, r.status_code, r.content, args['access_token']
    return json.loads(r.content)



app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_object('conf.Config')
app.secret_key = SECRET_KEY


def get_token(relative_url):
    access_token = session.get('access_token', None)

    if not access_token and 'code' in request.args:
        params = {
            'client_id': FB_APP_ID,
            'client_secret': FB_APP_SECRET,
            'redirect_uri': request.url_root.rstrip('/') + relative_url,
            'code': request.args['code']
        }

        from urlparse import parse_qs
        r = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        access_token = parse_qs(r.content)['access_token'][0]
        session['access_token'] = access_token

    perms = fb_call('me/permissions',
                    args={'access_token': access_token})
    if 'data' in perms and perms['data'][0].get('user_events', None):
        return access_token

    return False

    # cookie_key = 'fbsr_{0}'.format(FB_APP_ID)

    # if cookie_key in request.cookies:

    #     c = request.cookies.get(cookie_key)
    #     encoded_data = c.split('.', 2)

    #     sig = encoded_data[0]
    #     data = json.loads(urlsafe_b64decode(str(encoded_data[1])))

    #     if not data['algorithm'].upper() == 'HMAC-SHA256':
    #         raise ValueError('unknown algorithm {0}'.format(data['algorithm']))

    #     h = hmac.new(FB_APP_SECRET, digestmod=hashlib.sha256)
    #     h.update(encoded_data[1])
    #     expected_sig = urlsafe_b64encode(h.digest()).replace('=', '')

    #     if sig != expected_sig:
    #         raise ValueError('bad signature')

    #     code =  data['code']

    #     params = {
    #         'client_id': FB_APP_ID,
    #         'client_secret': FB_APP_SECRET,
    #         'redirect_uri': '',
    #         'code': data['code']
    #     }

    #     from urlparse import parse_qs
    #     r = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
    #     token = parse_qs(r.content).get('access_token')

    #    return token

def auth_redirect(relative_url):
    return redirect('https://www.facebook.com/dialog/oauth?'
                    'client_id=%s'
                    '&redirect_uri=%s'
                    '&scope=user_events,create_event'
                    % (FB_APP_ID, request.url_root.rstrip('/') + relative_url))

@app.route('/', methods=['GET', 'POST'])
def index():
    access_token = access_token = session.get('access_token', None)
    return render_template('whentomeet.html')

    if access_token:

        me = fb_call('me', args={'access_token': access_token})
        # fb_app = fb_call(FB_APP_ID, args={'access_token': access_token})
        # likes = fb_call('me/likes',
        #                 args={'access_token': access_token, 'limit': 4})
        # friends = fb_call('me/friends',
        #                   args={'access_token': access_token, 'limit': 4})
        # photos = fb_call('me/photos',
        #                  args={'access_token': access_token, 'limit': 16})

        # redir = request.url_root + 'close/'
        # POST_TO_WALL = ("https://www.facebook.com/dialog/feed?redirect_uri=%s&"
        #                 "display=popup&app_id=%s" % (redir, FB_APP_ID))

        # app_friends = fql(
        #     "SELECT uid, name, is_app_user, pic_square "
        #     "FROM user "
        #     "WHERE uid IN (SELECT uid2 FROM friend WHERE uid1 = me()) AND "
        #     "  is_app_user = 1", access_token)

        # SEND_TO = ('https://www.facebook.com/dialog/send?'
        #            'redirect_uri=%s&display=popup&app_id=%s&link=%s'
        #            % (redir, FB_APP_ID, request.url_root))

        url = request.url

        return render_template(
            'index.html', app_id=FB_APP_ID, token=access_token, likes=likes,
            friends=friends, photos=photos, app_friends=app_friends, app=fb_app,
            me=me, POST_TO_WALL=POST_TO_WALL, SEND_TO=SEND_TO, url=url,
            channel_url=channel_url, name=FB_APP_NAME)
    else:
        #return render_template('login.html', app_id=FB_APP_ID, token=access_token, url=request.url, channel_url=channel_url, name=FB_APP_NAME)
        return render_template('whentomeet.html')

@app.route('/auth/', methods=['GET'])
def authenticate():
    if session.get('oauth.state') != request.args.get('state'):
        abort(401)
    if request.args.get('error') == 'access_denied':
        return redirect(request.url_root)

    access_token = get_token()
    if not access_token:
        return auth_redirect(url_for('auth'))
    me = fb_call('me', args={'access_token': access_token})
    session['user.id'] = int(me['id'])
    return redirect(request.url_root + 'create/')


@app.route('/create/', methods=['GET', 'POST'])
def create():
    access_token = get_token(url_for('create'))
    if not access_token:
        return auth_redirect(url_for('create'))
    if 'code' in request.args:
        return redirect(url_for('create'))

    events = fb_call('me/events',
                     args={'access_token': access_token})

    if request.method == 'POST':
        event_id = int(request.form['fb-event-id'])
        times = json.loads(request.form['fb-times'])
        return redirect(url_for('vote', event_id=event_id))

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = ["12 AM", "1 AM", "2 AM", "3 AM", "4 AM", "5 AM", "6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM",
        "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM", "10 PM", "11 PM"]
    return render_template('schedule.html', title='Schedule an event',
                            events=events['data'],
                            days=days, times=times)


@app.route('/vote/<int:event_id>/', methods=['GET', 'POST'])
def vote(event_id):
    access_token = get_token(url_for('vote', event_id=event_id))
    if not access_token:
        return auth_redirect(url_for('vote', event_id=event_id))
    if 'code' in request.args:
        return redirect(url_for('vote', event_id=event_id))

    events = fb_call('me/events',
                     args={'access_token': access_token})

    days = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    times = ["12 AM", "1 AM", "2 AM", "3 AM", "4 AM", "5 AM", "6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM",
        "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM", "6 PM", "7 PM", "8 PM", "9 PM", "10 PM", "11 PM"]
    available = [[],[6],[5,6],[3,4,5,6,7,8,9,10,11,12,13],[2,3,4,5,6,7,11,12,13],[1,2,11,12],[]]
    return render_template('schedule.html', title='Schedule an event',
                            events=events['data'],
                            event_id=event_id,
                            days=days, times=times,
                            available=available)


@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')


@app.route('/close/', methods=['GET', 'POST'])
def close():
    return render_template('close.html')

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))

    configured = True
    def require(conf):
        if not app.config.get(conf):
            print ('Cannot start application without %s set' % conf)
            configured = False
    require('SECRET_KEY')
    require('FB_APP_ID')
    require('FB_APP_SECRET')

    if configured:
        app.run(host='0.0.0.0', port=port)
    else:
        exit(1)
