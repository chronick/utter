utter
=====

analysis of mediation utterances using levenshtein distance

This script will calculate the levenshtein distance 
for a given window against mediation data used in

__Donohue, Sherry, Idzik, Walsh. Interactive Framing in Divorce Mediation__

A link to the paper is forthcoming, pending publication.

Input Files:
-----
The input csv should follow the following format:

	[Trans #] [Turn] [Speaker] [Mean] [Mode] [High] [Low] [Frame In] [Frame Out]

these are all considered 'data columns'

Output Files:
-----
This version will create an output file for each data column 
in a user-specified directory with the following naming convention:

[transcipt\_id]\_[column\_name].csv

thus creating [number of transcripts] \* 6 output files (since there are 6 data columns)

if no directory is specified on the command line, 
a directory called 'out' will be created in the current directory.

Example:
-----
	utter.py -w 111,222,333 -f input.csv -o outputs

*NOTE: This has been developed and tested in python 2.7.* 

