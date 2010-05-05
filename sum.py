#!/usr/bin/env python

# Finds the sum of a specific column of a given file

import sys
import utilities

if len(sys.argv) < 3:
   print 'This utility computes the sum a given column of data in given data files.\n'
   print 'Usage: sum.py file1 file2 ... filen column'
   sys.exit()

list = []
   
try:
   column = int(sys.argv[len(sys.argv)-1])
except ValueError:
   print 'Usage: sum.py file1 file2 ... filen column'
   print str(sys.argv[len(sys.argv)-1]) + ' is not an integer!'
   sys.exit()

sum = 0
for x in range(len(sys.argv)-2):
   y = x + 1
   try:
      file = open(sys.argv[y],'r')
   except IOError:
      print 'Usage: sum.py file1 file2 ... filen column'
      print sys.argv[y] + ' could not be opened!'
      continue
   
   for line in file:
      words = line.split()
      if len(words) < column:
         continue
      try:
         sum = sum + float(words[column - 1])
      except ValueError:
         continue
   
   file.close()
   
print 'The sum of column ' + str(column) + ' is: ' + str(sum)
