# -*- coding: utf-8 -*-

from __future__ import unicode_literals

import datetime
import os
import json

from flask import Flask, session, request, redirect, render_template, url_for
import requests
requests = requests.session()

from models import db, Event, Vote

__all__ = ['app']


def fb_call(call, args=None):
    url = "https://graph.facebook.com/{0}".format(call)
    r = requests.get(url, params=args)
    # print r.url, r.status_code, r.content, args['access_token']
    return json.loads(r.content)


app = Flask(__name__)
app.config.from_object('conf.Config')
db.init_app(app)


def get_token(relative_url):
    access_token = session.get('access_token', None)

    if not access_token and 'code' in request.args:
        params = {
            'client_id': app.config['FACEBOOK_APP_ID'],
            'client_secret': app.config['FACEBOOK_SECRET'],
            'redirect_uri': request.url_root.rstrip('/') + relative_url,
            'code': request.args['code']
        }

        from urlparse import parse_qs
        r = requests.get('https://graph.facebook.com/oauth/access_token', params=params)
        access_token = parse_qs(r.content)['access_token'][0]
        session['access_token'] = access_token

#    perms = fb_call('me/permissions',
#                    args={'access_token': access_token})
#    if 'data' in perms and perms['data'][0].get('user_events', None):
#        return access_token

    return access_token

def auth_redirect(relative_url):
    return redirect('https://www.facebook.com/dialog/oauth?'
                    'client_id=%s'
                    '&redirect_uri=%s'
                    '&scope=user_events'
                    % (app.config['FACEBOOK_APP_ID'], request.url_root.rstrip('/') + relative_url))


@app.route('/', methods=['GET', 'POST'])
def index():
    access_token = access_token = session.get('access_token', None)
    return render_template('whentomeet.html')


def days():
    return [(datetime.date.today() + datetime.timedelta(i)).strftime("%A,<br>%b %d")
            for i in xrange(7)]

times = ["12 AM", "1 AM", "2 AM", "3 AM", "4 AM", "5 AM",
    "6 AM", "7 AM", "8 AM", "9 AM", "10 AM", "11 AM",
    "12 PM", "1 PM", "2 PM", "3 PM", "4 PM", "5 PM",
    "6 PM", "7 PM", "8 PM", "9 PM", "10 PM", "11 PM"]


@app.route('/create/', methods=['GET', 'POST'])
def create():
    access_token = get_token(url_for('create'))
    if not access_token:
        return auth_redirect(url_for('create'))
    if 'code' in request.args:
        return redirect(url_for('create'))

    me = fb_call('me',
                 args={'access_token': access_token})

    if request.method == 'POST':
        event_id = int(request.form['fb-event-id'])
        available = request.form['fb-times']
        event = Event(event_id, me['id'], available)
        db.session.add(event)
        db.session.commit()
        return redirect(url_for('vote', event_id=event.id))

    events = fb_call('me/events',
                     args={'access_token': access_token})

    return render_template('schedule.html', title='When Works',
                            events=events['data'],
                            days=days(), times=times)


def aggregate_votes(votes, user_ids):
    result = [[0]*24 for i in xrange(7)]
    usersbytime = [[[] for i in xrange(24)] for j in xrange(7)]
    top = 0
    for v, vote in enumerate(votes):
        for d, day in enumerate(vote):
            for time in day:
                usersbytime[d][time].append(user_ids[v][0])
                result[d][time] += 1
                top = max(top, result[d][time])
    return result, usersbytime, float(top)


@app.route('/vote/<int:event_id>/', methods=['GET', 'POST'])
def vote(event_id):
    access_token = get_token(url_for('vote', event_id=event_id))
    if not access_token:
        return auth_redirect(url_for('vote', event_id=event_id))
    if 'code' in request.args:
        return redirect(url_for('vote', event_id=event_id))

    event = Event.query.filter_by(id=event_id).first()
    available = json.loads(event.available)

    me = fb_call('me',
                 args={'access_token': access_token})

    if request.method == 'POST':
        vote = Vote(me['id'], me['name'], event_id, request.form['fb-times'])
        db.session.add(vote)
        db.session.commit()
        return redirect(url_for('vote', event_id=event_id))

    #events = fb_call('me/events',
    #                 args={'access_token': access_token})

    votes = Vote.query.filter_by(event=event_id).all()
    users = [(vote.user_id, vote.user_name) for vote in votes]
    votejson = [json.loads(vote.vote) for vote in votes]
    results, usersbytime, top = aggregate_votes(votejson, users)

    used_times = [False]*24
    for i in xrange(24):
        for l in available:
            if i in l:
                used_times[i]=True
    return render_template('schedule.html', title='Schedule an event',
                            #events=events['data'],
                            event_id=event_id,
                            days=days(),
                            times=times, used_times=used_times,
                            available=available, usersbytime=usersbytime,
                            users=users,
                            results=results, top=top or 1)


@app.route('/channel.html', methods=['GET', 'POST'])
def get_channel():
    return render_template('channel.html')


@app.route('/close/', methods=['GET', 'POST'])
def close():
    return render_template('close.html')
