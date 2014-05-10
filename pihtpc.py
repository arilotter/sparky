#!/usr/bin/env python3.4

# dotslash for local
from flask import Flask, render_template, request, redirect
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from omxplayer import OMXPlayer
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
import os
import traceback
import re
app = Flask(__name__)
app.debug = False  # debug! set to false for prod.

base_path = '.'  # sets the script's base directory for files/folders
tmp_path = base_path + '/tmp'
torrent_fifo = tmp_path + '/torrent_fifo'
player = None

# this regex is to escape terminal color codes.
ansi_escape = re.compile(r'\x1b[^m]*m')


@app.route('/about')
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


@app.route('/remote/send_key/<command>')  # sending keys from the remote
def send_key(command):
    if command == 'left':
        keystroke = '\x1B\x5B\x44'  # keycode for left
    elif command == 'right':
        keystroke = '\x1B\x5B\x43'  # keycode for right
    else:
        keystroke = command
    send_input_to_omxplayer(keystroke)
    return '', 204  # 204 means success but no content. it worked :3


@app.route('/remote/play_pause')
def play_pause():
    player.toggle_pause()
    return 'dong'


@app.route('/play', methods=['GET'])
def play_url():
    url = request.args.get('url')  # grab url from /play?url=*

    if not url.startswith('http'):  # in case the user forgot it
        print('url missing http/wrong protocol')
        url = 'http://' + url  # let's assume it's http, not https

    print('recieved url %s' % url)
    print('requesting headers from %s...' % url)
    req = Request(url)
    req.get_method = lambda: 'HEAD'  # only request headers, no content
    response = urlopen(req)
    content_type = response.headers['content-type']
    content_type_split = content_type.split('/')  # split into 2 parts
    print('headers recieved. content type is %s' % content_type)

    try:
        if content_type_split[0] == 'audio' or url_split[0] == 'video':
            print('url was raw media file, playing! :)')
            play_omxplayer(url)
        elif content_type_split[1] == 'x-bittorrent':
            print('loading btcat for further processing')
            # this isn't implemented yet.

        elif content_type_split[0] == 'text':
            print('loading youtube-dl for further processing')
            ydl = YoutubeDL({'outtmpl': '%(id)s%(ext)s'})
            ydl.add_default_info_extractors()
            result = ydl.extract_info(url, download=False)
            if 'entries' in result:
                video = result['entries'][0]
            else:
                video = result
            play_omxplayer(video['url'])
        else:
            raise DownloadError('Invalid filetype: not audio, video, or text.')

        return '', 204  # success w/ no response!
    except (UnicodeDecodeError, DownloadError) as e:
        return ansi_escape.sub('', str(e)), 400  # send error message


def play_omxplayer(uri):
    print('playing %s in omxplayer...' % uri)
    player = OMXPlayer(uri, args='-b -r --audio_queue=10 --video_queue=40')
    print('playing successful')


def send_input_to_omxplayer(key):
    input_fifo = tmp_path + '/input_fifo'
    if not os.path.isfile(input_fifo):
        os.mkfifo(input_fifo)
    f = open(input_fifo, 'w')
    f.write(key)

if __name__ == '__main__':
    app.run()
