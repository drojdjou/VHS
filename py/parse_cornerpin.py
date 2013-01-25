#!/usr/bin/env python

"""Parse tracking data

USAGE: ./parseTrackingData data-file.txt save-to-file.txt

Works with Corner Pin data files"""

import sys, os, re

pinstartPattern = "Effects	ADBE"
widthPattern = "Source Width"
heightPattern = "Source Height"
size = [0,0]

def main(inpath, outdir):
	outpath = os.path.join(outdir, os.path.split(inpath)[1]);

	fin = open(inpath, 'r')
	fout = open(outpath, 'w')

	for line in fin:
		if pinstartPattern in line:
			fout.write("POINT: %s\n" % line.split()[-1])
		elif widthPattern in line:
			size[0] = float(line.strip().split()[-1])
		elif heightPattern in line:
			size[1] = float(line.strip().split()[-1])
		else:
			p = re.match(r'^\s*([\d\.]+)\s*(-*[\d\.]+)\s*(-*[\d\.]+)$', line, re.MULTILINE)
			if p:
				w = float(p.group(2)) / size[0]
				h = float(p.group(3)) / size[1]
				fout.write("%s %.4f %.4f\n" % (p.group(1), w, h))
				

	fin.close()
	fout.close()

if __name__ == '__main__':
	if len(sys.argv) < 3:
		print __doc__
	else:
		main(sys.argv[1], sys.argv[2])
