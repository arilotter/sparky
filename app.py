from flask import Flask, render_template, request
from urllib.request import urlopen
from movie_scraper import get_streaming_url
from urllib.parse import urlparse
from omxplayer import OMXPlayer
import os
app = Flask(__name__)

#woohooo vars
base_path = 'C:/Users/Demo/Desktop/ari' #woohoooo portability
tmp_path = base_path + '/tmp'
torrent_fifo = tmp_path + '/torrent_fifo'
player = None

#video_exts = ['3gp', 'avchd', 'avi', 'flv', 'm2v', 'm4v', 'mkv', 'mov', 'mpeg', 'mpg', 'ogg', 'wmv']

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
	
@app.route('/play', methods=['GET'])
def play_url():
	url = request.args.get('url')
	req = urlopen(url)
	type = req.headers['content-type'].split('/')[0]
	
	if type == "audio" or type == "video":
		play_omxplayer(url)
	elif type == "text": #let's assume it's a streaming movie?
		if is_streaming_movie(req):
			play_omxplayer(get_streaming_url(url))
		elif is_youtube_video(url): #pass url cause youtube is just a url
			pass
	else:
		return 'wtf rong url', 400 #u donged up man
	return '', 204 # success! :D

	
def is_streaming_movie(req):
	return ("var flashvars = {};" in req.read().decode('utf-8'))
	
def is_youtube_video(url):
	domain = '.'.join(urlparse(url).netloc.split('.')[-2:])
	return (domain == "youtube")

def play_omxplayer(uri):
	player = OMXPlayer(uri, args='-b -r --audio_queue=10 --video_queue=40')
	print(args)
	
def send_input_to_omxplayer(input): #wow this should actually work :D
	input_fifo = tmp_path + '/input_fifo'
	if not os.path.isfile(input_fifo):
		os.mkfifo(input_fifo)
	f = open(input_fifo, 'w')
	f.write(input)
	
if __name__ == "__main__":
	app.run(debug=True) #DEBOOG