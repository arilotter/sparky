#!./bin/python3.4
# dotslash for local
from flask import Flask, render_template, request
from urllib.request import urlopen, Request
from urllib.parse import urlparse
from omxplayer import OMXPlayer
from youtube_dl import YoutubeDL
from youtube_dl.utils import DownloadError
import os
import traceback
import re
app = Flask(__name__)

#woohooo vars
base_path = '.' #woohoooo portability
tmp_path = base_path + '/tmp'
torrent_fifo = tmp_path + '/torrent_fifo'
player = None

ansi_escape = re.compile(r'\x1b[^m]*m')

@app.route('/')
def splash():
	return render_template('splash.html')

@app.route('/remote/')
def remote(): #woooo
	return render_template('remote.html')
	
@app.route('/remote/send_key/<key>') #sending keys from the remote
def send_key(key):
	if key == 'left':
		input = '\x1B\x5B\x44'
	elif key == 'right':
		input = '\x1B\x5B\x43'
	else:
		input = key
	send_input_to_omxplayer(input)
	return '', 204 #204 means success but no content. it worked :3

@app.route('/remote/play_pause')
def play_pause():
	player.toggle_pause()
	return 'dong'
	
@app.route('/play', methods=['GET'])
def play_url():
	url = request.args.get('url')
	if not url.startswith('http'): #gets https too :D
		print('url missing http/wrong protocol')
		#Let's assume it's http, not https (kek)
		url = 'http://' + url
	print('looking up url %s' % url)
	req = Request(url)
	req.get_method = lambda : 'HEAD'
	response = urlopen(req)
	type = response.headers['content-type'].split('/')[0]
	try:
		if type == 'audio' or type == 'video':
			play_omxplayer(url)
		elif type == 'text': 
			print('page type is text, loading youtubeDL for further processing')
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
				
		return '', 204 # success! :D but ff doesn't like 204s :c
	except (UnicodeDecodeError, DownloadError) as e:
		return ansi_escape.sub('', str(e)), 400		

def play_omxplayer(uri):
	print('playing %s in omxplayer' % uri)
	player = OMXPlayer(uri, args='-b -r --audio_queue=10 --video_queue=40')
	print('launched successfully')
	
def send_input_to_omxplayer(input): #wow this should actually work :D
	input_fifo = tmp_path + '/input_fifo'
	if not os.path.isfile(input_fifo):
		os.mkfifo(input_fifo)
	f = open(input_fifo, 'w')
	f.write(input)
	
if __name__ == '__main__':
	app.run('0.0.0.0', debug=True,) #DEBOOG
