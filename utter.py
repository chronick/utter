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

from optparse import OptionParser

#######################################################

parser = OptionParser()

parser.add_option(	"-v", "--verbose", 
					dest="verbose",default=False,
					help="make verbose"
					)

parser.add_option(	"-f", "--file", 
					dest="filename",action="store",
					help="use input file"
					)         

parser.add_option(	"-o", "--output", 
					dest="output",action="store",
					help="specify output file name"
					)         

parser.add_option(	"-w", "--window", 
					dest="window",action="store",
					help="specify the window to compare to"
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
	def __init__(self, id = 0, owner = '', type = 0):
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
	
	def set_id(self, id):
		self.id = id
	
	def add_utterance(self, utterance):
		self.utterances.append(utterance)
	
	def get_utterance_type_list(self):
		return [u.type for u in self.utterances]
	
	def get_type_windows(self, window_size):
		t = self.get_utterance_type_list()
		window_list = []
		for c in range(len(t) - window_size):
			window_list.append(''.join(t[c:c+window_size]))
		return window_list
	
	def calculate_synchrony(self, comp_str):
		l = len(comp_str)
		tw = self.get_type_windows(l)
		out = []
		for w in tw:
			out.append(LevDist(w,comp_str))
		return out


#######################################################

def debug(debug_string):
	if options.verbose: print debug_string

#######################################################

def main():

	uReader = csv.reader(open(options.filename, 'r'), delimiter = ',')
	uWriter = csv.writer(open(options.output,'w'), delimiter = ',')


	sessions = []
	current_id = ''
	current_sesh = Session()

	for i in uReader:

		if i[0] != current_id: # we're on a new sesh. good times abide.
			debug('current: %s	new: %s'%(current_id, i[0]))
			current_sesh.set_id(current_id)
			sessions.append(current_sesh)
			current_id = i[0]
			current_sesh = Session()

		else: # we're still on the old sesh.
			current_sesh.add_utterance(Utterance(id = i[2], owner = i[1], type = i[3]))

	# last session 
	current_sesh.set_id(current_id)
	sessions.append(current_sesh) 
			
	print [s.id for s in sessions]
	
	for ws in [[s.id] + s.calculate_synchrony(options.window) for s in sessions[1::]]:
		uWriter.writerow(ws) 	

if __name__ == '__main__':
	main()
