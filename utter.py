#!/usr/bin/env python

#
#  	utter.py
#	Levenshtein analysis of mediation utterances
#
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; version 2
#  of the License.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
#


import csv
import os,sys
import os.path as path

from optparse import OptionParser

def store_window_list(option, opt, value, parser):
	"""Callback for storing the window list. 
		Needs to go here for the option parser."""
	a = value.split(",")
	parser.values.windows = a
	parser.values.window = a[0]

#######################################################

usage  = """%prog [-v] -w [window] -f [input_file].csv

This script will calculate the levenshtein distance 
for a given window against mediation data used in {PAPER}.

Input Files:
	The input csv should follow the following format:
	[transcript #] [turn] [speaker ID] [mean] [mode] [high] [low] [Frame In] [Frame Out]

	mean,mode,high,low,framein,frameout are all considered 'data columns'

Output Files:
	This version will create an output file for each data column 
	in a user-specified directory with the following naming convention:

	[transcipt_id]_[column_name].csv

	thus creating [number of transcripts] * 6 output files (since there are 6 data columns)

	if no directory is specified on the command line, 
	a directory called 'out' will be created in the current directory.

Example:
	%prog -w 111,222,333 -f input.csv

NOTE: This has been developed and tested in python 2.7. 
	It will probably work in 2.5-6, but just FYI
"""
		
parser = OptionParser(usage)

parser.add_option(	"-v", "--verbose", 
					dest="verbose",
					default=False,
					help="make verbose"
					)

parser.add_option(	"-f", "--file", 
					dest="filename",
					action="store",
					help="use input file"
					)         

parser.add_option(	"-o", "--output_dir", 
					dest="output_dir",
					action="store",
					default="./out",
					help="specify output directory"
					)         

parser.add_option(	"-w", "--window", 
					dest="window",
					action="callback", 
					callback=store_window_list, 
					type="string",
					help="specify the window(s) to compare to"
					)         


(options,args) = parser.parse_args()


#######################################################


def listprintstr(astr):
	return '  '.join(list(astr))

def printLevDistMatrix(str1,str2,d):
	print "     ",listprintstr(str1)
	for i in range(len(d)):
		print (" "+str2)[i],'['+'  '.join([str(a) for a in d[i]])+']'

def LevDist(str1,str2,debug=False):
	d = []
	m = len(str1)
	n = len(str2)

	for i in range(n+1):
		d.append([])
		for i in range(m+1):
			d[-1].append(0)
	
	for i in range(m+1):
		d[0][i] = i

	for j in range(n+1):
		d[j][0] = j
	
	for j in range(1,m+1):
		for i in range(1,n+1):

			if str1[j-1] == str2[i-1]:
				d[i][j] = d[i-1][j-1]
			else:
				d[i][j] = min(
							d[i-1][j] + 1,
							d[i][j-1] + 1,
							d[i-1][j-1] + 1
							)

	if debug:
		printLevDistMatrix(str1,str2,d)
	
	return d[n][m]

class Utterance(object):
	"""utterance data structure."""
	def __init__(self, id = 0, owner = '', type = [0,]):
		super(Utterance, self).__init__()

		self.id = id
		self.owner = owner
		self.type = type
		
class Session(object):
	"""Mediation session object. Stores collections of utterances."""
	def __init__(self, id = ''):
		super(Session, self).__init__()

		self.id = id
		self.utterances = []
	
	def __str__(self):
		return "Session object with id: %s"%(self.id)
	
	def set_id(self, id):
		self.id = id
	
	def add_utterance(self, utterance):
		self.utterances.append(utterance)
	
	def get_utterance_type_list(self,index = 0):
		return [u.type[index] for u in self.utterances]
	
	def get_type_windows(self, window_size, type_index = 0):
		t = self.get_utterance_type_list(type_index)
		window_list = []
		for c in range(len(t) - (window_size-1)):
			window_list.append(''.join(t[c:c+window_size]))
		return window_list
	
	def calculate_synchrony(self, comp_str, type_index = 0):
		l = len(comp_str)
		tw = self.get_type_windows(l,type_index)
		out = []
		for w in tw:
			out.append(LevDist(w,comp_str))
		return out


#######################################################

def debug(debug_string):
	if options.verbose: print debug_string

#######################################################

def main():

	if not path.exists(options.output_dir):
		os.mkdir(path.abspath(options.output_dir))

	uReader = csv.DictReader(open(options.filename, 'r'), delimiter = ',')

	mmhlff = ["mean","mode","high","low","frame-in","frame-out"]

	sessions = []
	current_id = ''
	current_sesh = Session()

	for i in uReader:

		if i['Trans #'] != current_id: # we're on a new sesh. good times abide.
			debug('current: %s	new: %s'%(current_id, i['Trans #']))
			current_sesh.set_id(current_id)
			sessions.append(current_sesh)
			current_id = i['Trans #']
			current_sesh = Session()

		current_sesh.add_utterance(
			Utterance(	id = i['Turn'], owner = i['Speaker'], 
						type = [i['Mean'],i['Mode'],i['High'],i['Low'],i['Frame In'],i['Frame Out']]))

		#print current_id, i['Turn']

	# last session 
	current_sesh.set_id(current_id)
	sessions.append(current_sesh) 
			
	print [s.id for s in sessions]

	for s in sessions[1::]:
		for col in range(6):
			#print 'current session:', s
			filename =  s.id+"_"+mmhlff[col]+'.csv'
			outfile = open(path.join(options.output_dir,filename),'w')
			uWriter = csv.writer(outfile, delimiter = ',')
			uWriter.writerow(options.windows)

			# now we start calculating synchrony for each window

			synchs = []

			for window in options.windows:
				#print window
				synchs.append(s.calculate_synchrony(window,col))

			ch = len(synchs[0])

			a = []
			l = len(synchs[0])
			for i in range(len(synchs[0])):
				for x in synchs:
					a.append(x[i])
			
				uWriter.writerow(a)
				a = []

	

if __name__ == '__main__':
	main()
