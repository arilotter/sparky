#!/usr/bin/env python3
from urllib.request import urlopen, Request
from urllib.parse import urlencode
import sys
import re

def get_flashvar(flashvar, html):
    return re.search("flashvars." + flashvar + "=\"(.+)\";", html).group(1)

def filekey(html):
    filekey = re.search("flashvars.filekey=(.+);", html).group(1)
    if not '"' in filekey:
        filekey = re.search("var " + filekey + "=\"(.+)\";", html).group(1)
    else:
        filekey = filekey.replace('"',"") #strip quotes if it was quoted.
    return filekey

    
#video_url = "http://www.novamov.com/video/51e68fdb9566b" #testing known working url

def get_streaming_url(url):
	html = urlopen(url).read().decode("utf-8")

	# start building request now.
	domain = get_flashvar("domain", html)

	request_headers = { #for some reason, setting the user agent makes it not fail. lel.
		'User-Agent' : 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/34.0.1847.131 Safari/537.36'
	}

	request_parems = {
		"file" : get_flashvar("file", html),
		"key" : filekey(html),
		"user" : "undefined",
		"pass" : "undefined",
		"cid" : get_flashvar("cid", html),
		"cid2" : "undefined",
		#"cid3" : "undefined",
		"numOfErrors" : 0
	}

	request_url = "%s/api/player.api.php?%s" % (domain, urlencode(request_parems))
	request = Request(request_url, headers=request_headers)
	r_code = 0

	while not r_code == 200: #try again if you get a 500
		r = urlopen(request)
		r_code = r.getcode()

	video_html = r.read().decode("utf-8")

	flv_url = re.search("^url=(.+?)&", video_html).group(1)
	title = re.search("title=(.+?)&", video_html).group(1)
	return flv_url
