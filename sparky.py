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

player = None
title = None
last_logged_message = ""

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


@app.route('/remote/omxplayer/<command>')  # sending keys from the remote
def omxplayer_remote(command):
    player = get_player()
    if player is not None:
        getattr(player, command)()
        return '', 204
    else:
        return 'nothing playing', 400


@app.route('/remote/system/<command>')
def system_remote(command):
    if command == "reboot":
        log('rebooting!')
        os.system("sudo reboot")
    else:
        return 'bad command', 400
    return '', 204  # success!


@app.route('/status/')
def status():
    player = get_player()
    if player is not None:
        dictionary = {
            'video_loaded': True,
            'paused': player.paused,
            'now_playing': title
        }
        
    else:
        dictionary = {'video_loaded': False}
    
    return json.dumps(dictionary)


@app.route('/play', methods=['GET'])
def play_url():  # this only plays http urls for now, torrents soon.
    url = request.args.get('url')  # grab url from /play?url=*

    if not url.startswith('http'):  # in case the user forgot it
        log('url missing http/wrong protocol')
        url = 'http://' + url  # let's assume it's http, not https

    log('received url %s' % url)
    log('requesting headers from %s...' % url)
    req = Request(url)
    req.get_method = lambda: 'HEAD'  # only request headers, no content
    response = urlopen(req)
    ctype = response.headers['content-type']
    ctype_split = ctype.split('/')  # split into 2 parts
    log('headers received. content type is %s' % ctype)

    try:
        if ctype_split[0] == 'audio' or ctype_split[0] == 'video':
            log('url was raw media file, playing! :)')
            play_omxplayer(url)
        elif ctype_split[1] == 'x-bittorrent':
            log('loading torrents not implemented.')
            # this isn't implemented yet.
        elif ctype_split[0] == 'text':
            log('loading youtube-dl for further processing')
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

@app.route("/log/")
def gen_log():
    return get_last_logged_message()


def play_omxplayer(uri):
    log('playing %s in omxplayer...' % uri)
    global player
    if get_player() is not None:
        player.stop()
    player = OMXPlayer(uri,
                       args='-b -r --audio_queue=10 --video_queue=40',
                       start_playback=True)


def log(text):
    print("[sparky] %s" % text)
    
    global last_logged_message
    last_logged_message = text


def get_last_logged_message():
    global last_logged_message
    return last_logged_message


def get_player():
    global player
    if player is not None and player.has_finished():
        player = None
        title = None
    return player


if __name__ == '__main__':
    app.run("0.0.0.0", debug=True)
