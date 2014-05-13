#!/usr/bin/env python3.4

# dotslash for local
from flask import Flask, render_template, request, redirect
from werkzeug.contrib.fixers import ProxyFix
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from omxplayer import OMXPlayer
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
import os
import traceback
import re
import json

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app)

base_path = '.'  # sets the script's base directory for files/folders
player = None
title = None

# this regex is to escape terminal color codes.
_ANSI_ESCAPE_REXP = re.compile(r"\x1b[^m]*m")


@app.route('/about/')
def splash():
    return render_template('splash.html')


@app.route('/')
def root():  # redirect to remote for now, might change.
    return redirect('/remote')


@app.route('/remote/')
def remote():
    return render_template('remote.html')


@app.route('/settings/')
def settings():
    return render_template('settings.html')


@app.route('/remote/command/<command>')  # sending keys from the remote
def omx_input(command):
    player = get_player()
    if player is not None:
        getattr(player, command)()
        return '', 204
    else:
        return 'nothing playing', 400


@app.route('/status/')
def status():
    player = get_player()
    if player is not None:
        dictionary = {'video_loaded': True,
                      'paused': player.paused,
                      'now_playing': title
                      }
        return json.dumps(dictionary)
    else:
        return json.dumps({'video_loaded': False})


@app.route('/play', methods=['GET'])
def play_url():  # this only plays http urls for now, torrents soon.
    url = request.args.get('url')  # grab url from /play?url=*

    if not url.startswith('http'):  # in case the user forgot it
        print('url missing http/wrong protocol')
        url = 'http://' + url  # let's assume it's http, not https

    print('recieved url %s' % url)
    print('requesting headers from %s...' % url)
    req = Request(url)
    req.get_method = lambda: 'HEAD'  # only request headers, no content
    response = urlopen(req)
    ctype = response.headers['content-type']
    ctype_split = ctype.split('/')  # split into 2 parts
    print('headers recieved. content type is %s' % ctype)

    try:
        if ctype_split[0] == 'audio' or ctype_split[0] == 'video':
            print('url was raw media file, playing! :)')
            play_omxplayer(url)
        elif ctype_split[1] == 'x-bittorrent':
            print('loading btcat for further processing')
            # this isn't implemented yet.
        elif ctype_split[0] == 'text':
            print('loading youtube-dl for further processing')
            ydl = YoutubeDL({'outtmpl': '%(id)s%(ext)s', 'restrictfilenames': True})
            ydl.add_default_info_extractors()
            result = ydl.extract_info(url, download=False)
            if 'entries' in result:  # if video is a playlist
                video = result['entries'][0]  # play the 1st video in the playlist
            else:
                video = result
            play_omxplayer(video['url'])
            global title
            title = video['title']
        else:
            raise DownloadError('Invalid filetype: not audio, video, or text.')

        return '', 204  # success w/ no response!
    except (UnicodeDecodeError, DownloadError) as e:
        return _ANSI_ESCAPE_REXP.sub('', str(e)), 400  # send error message


def play_omxplayer(uri):
    print('playing %s in omxplayer...' % uri)
    global player
    if get_player() is not None:
        player.stop()
    player = OMXPlayer(uri,
                       args='-b -r --audio_queue=10 --video_queue=40',
                       start_playback=True)


def get_player():
    global player
    if player is not None and player.has_finished():
        player = None
        title = None
    return player


if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
