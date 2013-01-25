#!/usr/bin/env python

"""Parse tracking data

USAGE: ./parse_transform.py data-file.txt save-to-file.txt

Works with TRansform data files and exports an array of mat2 (2D matrices)"""

import sys, os, re, math

widthPattern = "Source Width"
heightPattern = "Source Height"

anchorPointStart = "Anchor Point"
positionStart = "Position"
scaleStart = "Scale"
rotationStart = "Rotation"

size = [0,0]

position = []
scale = []
rotation = []

def main(inpath, outpath):

	fin = open(inpath, 'r')

	dataType = "N"

	for line in fin:
		if "Frame" in line or "End" in line:
			continue

		if not line.strip():
			continue

		if anchorPointStart in line:
			dataType = "A"
			continue
		elif positionStart in line:
			dataType = "P"
			continue
		elif scaleStart in line:
			dataType = "S"
			continue
		elif rotationStart in line:
			dataType = "R"
			continue

		if widthPattern in line:
			size[0] = float(line.strip().split()[-1])
			print "Width: ", size[0]
			continue
		elif heightPattern in line:
			size[1] = float(line.strip().split()[-1])
			print "Height: ", size[1]
			continue

		if "A" in dataType or "N" in dataType:
			continue
			
		if "P" in dataType:
			# f = int(line.strip().split()[0])
			x = float(line.strip().split()[1])
			y = float(line.strip().split()[2])
			position.append(x)
			position.append(y)

		if "S" in dataType:
			# f = int(line.strip().split()[0])
			x = float(line.strip().split()[1]) / 100.0
			y = float(line.strip().split()[2]) / 100.0
			scale.append(x)
			scale.append(y)

		if "R" in dataType:
			# f = int(line.strip().split()[0])
			a = float(line.strip().split()[1])
			rotation.append(a)

	fin.close()

	fout = open(outpath, 'w')

	fout.write("{\n")
	fout.write("\t\"file\": \"%s\",\n" % inpath)
	

	for i in range(len(rotation)):
		tx = position[i*2]
		ty = position[i*2+1]

		if i == 0:
			otx = tx
			oty = ty

			orx = otx / size[0] * 2 - 1
			ory = oty / size[1] * 2 - 1

			fout.write("\t\"origin\": [%.5f, %.5f],\n" % (-orx, ory))
			fout.write("\t\"data\": [\n")

		tx = (tx - otx) / (size[0] * -0.5)
		ty = (ty - oty) / (size[1] * 0.5)

		sx = scale[i*2]
		sy = scale[i*2+1]

		r = -rotation[i] / 180.0 * math.pi

		c = math.cos(r)
		s = math.sin(r)

		fout.write("\t\t{\t\"m\":[%.5f, %.5f, %.5f, %.5f],\t\"t\": [%.6f, %.6f]\t}" % (c * sx, s * sx, -s * sy, c * sy, tx, ty))
		# fout.write("\t\t{\t\"m\":[%.5f, %.5f, %.5f, %.5f],\t\"t\": [%.6f, %.6f]\t}" % (sx, 0, 0, sy, tx, ty))

		if i < len(rotation) - 1:
			fout.write(",")
		fout.write("\n")

	fout.write("\t]\n}")
	fout.close()

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print __doc__
	else:
		main(sys.argv[1], sys.argv[2])
