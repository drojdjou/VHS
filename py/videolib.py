import os, sys, json, glob, shutil, math
from PIL import Image, ImageDraw

# HELPER VARAIABLES # # # # 
markerbits = 16
markerwidth = 16

black = (0,0,0)
white = (255,255,255)

VID = 1
FLV = 2

imageSize = (0, 0)

decode_cmd = 'ffmpeg -i %s -y -r 24 -s %ix%i -f image2 %s/%%04d.png'

# good with sound
encode_ffmpeg_cmd_sound = 'ffmpeg -y -i %(fld)s/%%04d.png -i %(audio)s -acodec libmp3lame -r %(fps)s -sameq -r %(fps)s %(mov)s'
# good without sound
encode_ffmpeg_cmd = 'ffmpeg -y -r %(fps)s -i %(fld)s/%%04d.png -sameq -r %(fps)s %(mov)s'

encode_webm_cmd = 'ffmpeg -y -r %(fps)s -i %(mov)s -codec:v libvpx -quality good -b:v %(btr)s -r %(fps)s -qmin 10 -qmax 42 -maxrate %(btr)s -bufsize 1200k %(webm)s'

#-ab %(btr)s  no audio in flv -g is key frame
# fps is set to 12 keyframe to 4 (-g) -q:v 5 qscale quality
encode_flv_cmd = 'ffmpeg -y -i %(fld)s/%%04d.png -r %(fps)s -g 4 -q:v 5 -f flv %(flv)s'

"""
Just to remember, these are settings HandBrakeCLI accepts
-e = encoder, use x264
-O = optiomize for HTTP streaming
-B = audio bitrate (unused)
-2 = use 2-pass
-T = turbo first pass
-r = set frame rate (not needed)
-q = quality (lower number == bigger file!) 
-b = video bitrate (this needs to be explored)
-E = audio encoder, lame or copy:mp3 
"""
encode_handbrake_cmd = 'HandBrakeCLI  --crop 0:0:0:0 --modulus 2 -r %(fps)s --input %(mov)s --output %(mpf)s -w %(hdw)s -l %(hdh)s -e x264 -O -q %(ql)i -2 -T'

# HELPER FUNCTIONS # # # # 

def encodeFrame(inImg, outImg, frame, conf):
	im = Image.open(inImg)

	#w = int(im.size[0] * 1 / conf['scale'])
	#h = int(im.size[1] * 1 / conf['scale'])

	w = conf['width']
	h = conf['height']

	# we don't resize anymore
	#im = im.resize((w,h), Image.ANTIALIAS)

	markersize = conf['barheight']
	barextenstion = 0 if markersize < 0 else markersize
	markersize = int(math.fabs(markersize))

	io = Image.new('RGB', (w, h + barextenstion), black)
	io.paste(im, (0, -conf['yoffset'], w, h - conf['yoffset']))

	# Add binary marker
	mrk = createMarker(frame, w, markersize)
	io.paste(mrk, (0, h + barextenstion - markersize, w, h + barextenstion))
	del mrk

	# Add frame number (should be optional)
	#frn = ImageDraw.Draw(io)
	#frn.text((w - 50, 10), str(frame))
	#del frn
	
	print "\033[2KProcessed frame %d to %s" % (frame, outImg)

	# io.save(outImg, "JPEG", quality=80)
	io.save(outImg, "PNG")

	del im
	del io

def rbin(x): 
	return ''.join(x & (1 << i) and '1' or '0' for i in range(markerbits-1,-1,-1))[::-1]

def createMarker(n, w, ms):
	bs = rbin(n)
	# print bs
	img = Image.new('RGB', (w, ms), black)
	draw = ImageDraw.Draw(img)

	bp = 0
	for b in bs:
		s = bp * markerwidth
		if bs[bp] == "1": draw.rectangle( [s, 0, s + markerwidth - 1, ms], fill=white)
		bp += 1

	del draw
	return img

def copySequencePart(conf, part, partsdir, markerdir):
	start = part[0]
	end = part[1]
	mode = part[2]
	dstname = part[3]

	global imageSize 

	print "Copying sequence part from %d to %d to %s" % (start, end, dstname)
	dstfolder = os.path.join(partsdir, dstname)
	os.mkdir(dstfolder)
	ct = 1
	for f in glob.glob("%s/*.*" % markerdir):
		if ct >= start and (ct <= end or end == -1): 

			if mode == VID or mode == FLV:
				filename = "%04d.%s" % (ct - start + 1, f[-3:])
				shutil.copyfile(f, os.path.join(dstfolder, filename))
			else:
				filename = "%04d.%s" % (ct, "jpg")
				img = Image.open(f)
				imageSize = img.size
				img.save(os.path.join(dstfolder, filename), "JPEG", quality=conf['jpegquality'])

		ct += 1
	return dstfolder

def encodeVideo(conf, part, partsdir):
	name = part[3]

	mov = "%s/%s.mov" % (conf['bin'], name)

	print "++++ Encoding mov %s using %s" % (mov, partsdir)
	
	if 'audio' in conf:
		ffmpegcmd = encode_ffmpeg_cmd_sound % {'audio':conf['audio'], 'fps':conf['fps'], 'fld':os.path.join(partsdir, name), 'mov':mov}
	else:
		ffmpegcmd = encode_ffmpeg_cmd % {'fps':conf['fps'], 'fld':os.path.join(partsdir, name), 'mov':mov}
	
	print special(ffmpegcmd)
	os.system(ffmpegcmd)

	for quality in conf['quality']:

		if len(conf['quality']) > 1:
			mp4 = "%s/%s_q%i.mp4" % (conf['bin'], name, quality)
		else:
			mp4 = "%s/%s.mp4" % (conf['bin'], name)

		print "++++ Encoding mp4 %s using %s" % (mp4, mov)
		hbrakecmd = encode_handbrake_cmd % {'fps':conf['fps'], 'hdw':imageSize[0], 'hdh':imageSize[1], 'mpf':mp4, 'mov':mov, 'ql':quality}
		print special(hbrakecmd)
		os.system(hbrakecmd)

	for bitrate in conf['bitrate']:			

		if len(conf['bitrate']) > 1:
			webm = "%s/%s_b%s.webm" % (conf['bin'], name, bitrate)
		else:
			webm = "%s/%s.webm" % (conf['bin'], name)

		print "++++ Encoding webm %s using %s" % (webm, mov)
		webmcmd = encode_webm_cmd % {'fps':conf['fps'], 'mov':mov, 'btr':bitrate, 'webm':webm}
		print special(webmcmd)
		os.system(webmcmd)

	# os.remove(mov)

def encodeFLV(conf, part, partsdir):
	name = part[3]

	flv = "%s/%s.flv" % (conf['bin'], name)

	print "++++ Encoding flv %s using %s" % (flv, partsdir)
	ffmpegcmd = encode_flv_cmd % {'fps':conf['fps'], 'fld':os.path.join(partsdir, name), 'flv':flv, 'btr':conf['flvbitrate'], 'qscale':6}
	print special(ffmpegcmd)
	os.system(ffmpegcmd)

# UTILITIES # # # # # 
codeCodes = {
	'black':	'0;30',		'bright gray':	'0;37',
	'blue':		'0;34',		'white':		'1;37',
	'green':	'0;32',		'bright blue':	'1;34',
	'cyan':		'0;36',		'bright green':	'1;32',
	'red':		'0;31',		'bright cyan':	'1;36',
	'purple':	'0;35',		'bright red':	'1;31',
	'yellow':	'0;33',		'bright purple':'1;35',
	'dark gray':'1;30',		'bright yellow':'1;33',
	'normal':	'0'
}

def special(text):
	return "\033["+codeCodes['cyan']+"m"+text+"\033[0m"
