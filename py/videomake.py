#!/usr/bin/env python

"""Video encoding/decoding script

Usage:
videomake.py path/to/conf_file.json command

A video make conf file is a JSON file with the following information:

{
	"video":"videofile.mov",
	"cache":"path_to_folder/",
	"bin":"path_to_folder/",
	"src":"path_to_folder/",
	"as3class":"path/to/Class.as",
	"width":1024,
	"height":576,
	"yoffset":2,
	"barheight":-4,
	"fps":23.98

	"parts": [
		[ 1, 120, "SEQ", "sequence-1"]
		[ 1, 130, "VID", "scene-1", 200]
	]
}

The elements of this file are:

video - the path to the original video file we are working with (mp4, mov or any other file ffmpeg knows will do)

cache - a path to a folder where the frames (image files) are stored

bin - a folder where the result files go (WARNING: make it a separate folder, not the same as folder where ex. original video is)

src/as3class - unless you use SEQ targets this settings do not matter

width, height - the width and height of the resulting video. This is applied during "process" phase.
	WARNING! Certain values can result in non-uniform scaling, be sure to know the original video size first!

barheight - how large should the bar be. 
	A positive number will add pixels and make the video larger, also changing the file dimensions
	However optimal video playback happens at certain dimensions, so sometimes it's better to keep video size intact and add the bar on top
	If this is the case, use a negative value - it will add the bar on top of the video in the botton (cropping the video a bit)
	Use this in conjunction with yoffset

yoffset - how much to offset the video vertically (makes sense if it is cropped with a negative barheight)
	It makes sense to have it = abs(barheight) / 2. Ex. if barheight = -4 than yoffset = 2
	If barheight is positive yoffset should be 0

fps - target FPS of the video (best to keep it same as the original FPS unless there is a reason not to do it that way)

parts - a list of parts of the video. The script can break the video into many shorter pieces, they can overlap.
		A part defines the:
		- start frame
		- end frame (if == -1 the it is assumed to be the last frame existing)
		- "VID" to encode and mp4 video or "SEQ" to encode as SWF image sequence
		- the name of the resuting file for this 

Commands are:

decode - take video and decode it into image sequence. Sequences are saved to cache/orig/
process - take the sequence from cache and process each frame into cache/marker/
encode - use parts to encode frames from cache/marker into the bin folder

"""

import os, sys, json, glob, shutil
import videolib
from PIL import Image, ImageDraw

# COMMAND FUNCTIONS # # # # 

def status(conf):
	print "Script called from %s" % os.getcwd()

	origdir = "%s/orig" % conf['cache']
	if not os.path.exists(origdir):
		print "%s directory does not exist" % origdir
	elif os.listdir(origdir) == "":
		print "%s directory is empty, video not decoded" % origdir
	else:
		print "%s directory exist and is full, video was decoded" % origdir

	markerdir = "%s/marker" % conf['cache']
	if not os.path.exists(markerdir):
		print "%s directory does not exist" % markerdir
	elif os.listdir(markerdir) == "":
		print "%s directory is empty, video not processed" % markerdir
	else:
		print "%s directory exist and is full, video was processed" % markerdir

def decode(conf):
	origdir = "%s/orig" % conf['cache']
	if os.path.exists(origdir):
		shutil.rmtree(origdir)
	os.makedirs(origdir)


	# dcmd = videolib.decode_cmd % (conf['video'], conf['fps'], conf['width'], conf['height'], origdir)
	dcmd = videolib.decode_cmd % (conf['video'], conf['width'], conf['height'], origdir)
	os.system(dcmd)

def process(conf):
	markerdir = "%s/marker" % conf['cache']
	if os.path.exists(markerdir):
		shutil.rmtree(markerdir)
	os.makedirs(markerdir)

	frame = 1
	origfld = "%s/orig/*.*" % conf['cache']
	print "Processing frames from %s" % origfld
	for f in glob.glob(origfld):
		fi = os.path.split(f)[1]
		fo = os.path.join(markerdir, "%s.png" % fi[:-4])
		videolib.encodeFrame(f, fo, frame, conf)
		frame += 1

def encode(conf):
	partsdir = "%s/parts" % conf['cache']

	# Just in case it was not cleaned up
	try:
		shutil.rmtree(partsdir)
	except Exception,e:
		pass

	markerdir = "%s/marker" % conf['cache']
	if not os.path.exists(markerdir):
		print "Can't encode - marker directory not found"
		quit()

	bindir = conf['bin']
	if not os.path.exists(bindir):
		os.makedirs(bindir)

	os.makedirs(partsdir)

	if len(sys.argv) > 3 and sys.argv[3] == "debug":
		debug = True
	else:
		debug = False

	for part in conf['parts']:
		if part[2] == 'VID': 
			part[2] = videolib.VID
		elif part[2] == 'FLV': 
			part[2] = videolib.FLV
		else: 
			part[2] = videolib.SEQ

		partdir = videolib.copySequencePart(conf, part, partsdir, markerdir)

		if part[2] == videolib.VID:
			videolib.encodeVideo(conf, part, partsdir)
		elif part[2] == videolib.FLV:
			videolib.encodeFLV(conf, part, partsdir)

	# shutil.rmtree(partsdir)

# MAIN # # # # # # # # # #

def main(args):
	conffile = open(args[0])
	try:
		conf = json.loads(conffile.read())
	except Exception, e:
		print "Error loading and parsing conf: %s" % e
		print "HINT: JSON decoder does not like trailing commas"
		quit()

	# Remove trailing commas from paths
	if conf['cache'][-1:] == "/":
		conf['cache'] = conf['cache'][:-1]

	if conf['bin'][-1:] == "/":
		conf['bin'] = conf['bin'][:-1]

	if args[1] == "decode":
		decode(conf)
	elif args[1] == "process":
		process(conf)
	elif args[1] == "encode":
		encode(conf)
	elif args[1] == "all":
		decode(conf)
		process(conf)
		encode(conf)
	elif args[1] == "status":
		status(conf)
	else:
		print "Unknown command %s" % args[1]

if __name__ == '__main__':
	if len(sys.argv) == 1:
		print __doc__
	else:
		main(sys.argv[1:])






