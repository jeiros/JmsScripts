#!/usr/bin/env python

# obligatory license -- this isn't sell-able anyway
"""
                           GPL LICENSE INFO

Copyright (C) 2012 Jason Swails

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 59 Temple Place - Suite 330,
Boston, MA 02111-1307, USA.
""" 

import sys, os

#~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+#

class RestartError(Exception):
   """ Raised if there's an error writing a restart file """
class Warning(Exception):
   """ You can catch this type of exception -- these are non-fatal """
class RestartWarning(Warning):
   """ If you do something I don't like with the restart... """

#~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+#

class AmberRestart(file):
   """ Amber Restart file has a fixed format """

   def write_title(self, title_string='Restart generated by %s' % 
                   (os.path.split(sys.argv[0])[1])):
      """ Writes the title of the restart file """
      if not hasattr(self, 'title_written'):
         self.write(title_string.strip() + os.linesep)
         self.title_written = True

   def write_header(self, natom, time=0.0):
      """ Writes the header of the file with natom, time """
      self.natom = natom
      if not hasattr(self, 'header_written'):
         self.write('%5d%15.7E' % (natom, time) + os.linesep)
         self.header_written = True

   def write_coordinate(self, x, y, z):
      """ Writes out the coordinates """
      if not hasattr(self, 'title_written'):
         raise RestartError('Write the title before writing coordinates!')
      if not hasattr(self, 'header_written'):
         raise RestartError('Write the header before writing coordinates!')
      if not hasattr(self, 'crd_num'): self.crd_num = 0
      self.write('%12.7F%12.7F%12.7F' % (x,y,z))
      self.crd_num += 1
      # Add a new line after every even coordinate
      if not self.crd_num % 2: self.write(os.linesep)

   def write_velocity(self, x, y, z):
      """ Writes out the velocities """
      if not hasattr(self, 'title_written'):
         raise RestartError('Write the title before writing velocities!')
      if not hasattr(self, 'header_written'):
         raise RestartError('Write the header before writing velocities!')
      if not hasattr(self, 'crd_num') or self.crd_num != self.natom:
         raise RestartError('Write all coordinates before writing velocities!')
      if not hasattr(self, 'vel_num'): self.vel_num = 0
      self.write('%12.7F%12.7F%12.7F' % (x,y,z))
      self.vel_num += 1
      # Add a new line after every even velocity
      if not self.vel_num % 2: self.write(os.linesep)

   def write_box_info(self, a, b, c, alpha=None, beta=None, gamma=None):
      """ Writes out the box information """
      if not hasattr(self, 'title_written'):
         raise RestartError('Write the title before writing box info!')
      if not hasattr(self, 'header_written'):
         raise RestartError('Write the header before writing box info!')
      if not hasattr(self, 'crd_num') or self.crd_num != self.natom:
         raise RestartError('Write all coordinates before writing box info!')
      # We don't need velocities to be a legitimate restart file
      if hasattr(self, 'box_info'):
         raise RestartWarning('Box information already present!')

      self.write('%12.7F%12.7F%12.7F' % (a, b, c))
      if not None in (alpha, beta, gamma):
         self.write('%12.7F%12.7F%12.7F' % (alpha, beta, gamma))

#~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+#

def main():
   import numpy
   from optparse import OptionParser, OptionGroup
   from Scientific.IO.NetCDF import NetCDFFile
   """ The main function """
   epilog = """This script will extract restart files from NetCDF trajectory
files and preserve any velocity information that may be present."""
   
   parser = OptionParser(epilog=epilog)
   parser.add_option('-y', '--netcdf', dest='inptraj', metavar='FILE',
                     help='Input NetCDF trajectory file to generate restarts ' +
                     'from', default=None)
   parser.add_option('-r', '--restrt', dest='restrt', metavar='FILE',
                     help='Name for output restart file. If multiple files ' +
                     'are created, a .# suffix will be added to this file ' +
                     'name where # is the frame number being dumped.')

   group = OptionGroup(parser, 'Single Restart File',
                       'This option will print a single restart file from the' +
                       ' desired frame of the trajectory')
   group.add_option('-f', '--frame', dest='frame', metavar='INT', type='int',
                    help='Frame number to convert to restart file', default=0)
   parser.add_option_group(group)

   group = OptionGroup(parser, 'Multiple Restart Files',
                       'These options will print multiple restart files from ' +
                       'the desired frames of the trajectory')
   group.add_option('-s', '--start-frame', dest='start', metavar='INT',
                    type='int', default=0,
                    help='First frame to turn into a restart')
   group.add_option('-e', '--end-frame', dest='end', metavar='INT',
                    type='int', default=0,
                    help='Last frame to turn into a restart')
   group.add_option('-i', '--interval', dest='interval', metavar='INT',
                    type='int', default=0,
                    help='Number of frames to skip between consecutive ' +
                    'restart files created.')
   parser.add_option_group(group)

   opt, arg = parser.parse_args()

   if arg:
      print 'Unrecognized command-line arguments!'
      parser.print_help()
      sys.exit(1)

   if not opt.inptraj:
      print 'No trajectory file given!'
      parser.print_help()
      sys.exit(1)

   # Make sure inptraj file exists
   if not os.path.exists(opt.inptraj):
      print 'Could not find NetCDF file %s!' % opt.inptraj
      sys.exit(1)

   # Make sure it's a NetCDF file
   try:
      traj = NetCDFFile(opt.inptraj)
   except IOError:
      print 'Cannot recognize %s! Is it a NetCDF File?' % opt.inptraj
      sys.exit(1)

   # Make sure no options are < 0 -- illegal options!
   for item in (opt.frame, opt.start, opt.end, opt.interval):
      if item < 0:
         print 'Illegal input options! All frames/intervals must be > 0!'
         sys.exit(1)

   # Make sure we didn't specify a single frame and a frame range
   if opt.frame > 0 and opt.start + opt.end + opt.interval > 0:
      print 'Single Frame selection and Frame range selection are'
      print 'mutually exclusive!'
      sys.exit(1)

   # Now do the single frame case
   if opt.frame:
      # Make sure we have enough frames...
      if opt.frame > len(traj.variables['coordinates']):
         print 'You asked for frame %d, but I can only find %d frames!' % (
               opt.frame, len(traj.variables['coordinates']))
         sys.exit(1)
      # Python indexes from 0 -- just subtract 1 now and save the headache
      # of doing it every time below...
      idx = opt.frame - 1
      # Now all is OK, so let's make the restart file
      rst_file = AmberRestart(opt.restrt, 'w')
      rst_file.write_title('File created by %s from %s trajectory.' % (
                           os.path.split(sys.argv[0])[1], opt.inptraj))
      rst_file.write_header(natom=traj.dimensions['atom'],
                            time=traj.variables['time'][idx])
      # Now write the coordinates
      for it in range(traj.dimensions['atom']):
         rst_file.write_coordinate(traj.variables['coordinates'][idx][it][0],
                                   traj.variables['coordinates'][idx][it][1],
                                   traj.variables['coordinates'][idx][it][2])
      # Now write the velocities
      if 'velocities' in traj.variables.keys():
         vels = traj.variables['velocities'][idx]
      else:
         print ('Warning: %s does not contain velocities. Setting all ' +
                'velocities to 0!') % opt.inptraj
         vels = numpy.zeros((traj.dimensions['atom'],3))

      # Now write the velocities
      for it in range(traj.dimensions['atom']):
         rst_file.write_velocity(vels[it][0], vels[it][1], vels[it][2])

      # Now write the box information if it's present
      if 'cell_lengths' in traj.variables.keys():
         a = traj.variables['cell_lengths'][idx][0]
         b = traj.variables['cell_lengths'][idx][1]
         c = traj.variables['cell_lengths'][idx][2]
         alpha, beta, gamma = None, None, None
         if 'cell_angles' in traj.variables.keys():
            alpha = traj.variables['cell_angles'][idx][0]
            beta = traj.variables['cell_angles'][idx][1]
            alpha = traj.variables['cell_angles'][idx][2]
         rst_file.write_box_info(a, b, c, alpha, beta, gamma)
      
      # Now we're done with our restart file -- close it
      rst_file.close()
      print 'Done creating restart file %s' % opt.restrt
      sys.exit(0)

   # Now, if we want to do multiple frames, check that our options are legal
   if opt.start > opt.end: 
      print 'Illegal start and end. Start must be less than End!'
      sys.exit(1)
   if opt.start > len(traj.variables['coordinates']):
      print 'Start frame is %d but there are only %d frames in %s!' % (
         opt.start, len(traj.variables['coordinates']), opt.traj)
      sys.exit(1)

   # Print out our warnings about missing velocities only once
   if not 'velocities' in traj.variables.keys():
      print ('Warning: %s does not contain velocities. Setting all ' +
             'velocities to 0!') % opt.inptraj

   # Print out all of the restart files
   for idx in range(opt.start-1, opt.end, opt.interval):
      rst_file = AmberRestart(opt.restrt + '.%d' % (idx+1), 'w')

      rst_file.write_title('File created by %s from %s trajectory.' % (
                           (os.path.split(sys.argv[0]))[1], opt.inptraj))
      rst_file.write_header(natom=traj.dimensions['atom'],
                            time=traj.variables['time'][idx])
      # Now write the coordinates
      for it in range(traj.dimensions['atom']):
         rst_file.write_coordinate(traj.variables['coordinates'][idx][it][0],
                                   traj.variables['coordinates'][idx][it][1],
                                   traj.variables['coordinates'][idx][it][2])
      # Now write the velocities
      if 'velocities' in traj.variables.keys():
         vels = traj.variables['velocities'][idx]
      else:
         vels = numpy.zeros((traj.dimensions['atom'],3))

      # Now write the velocities
      for it in range(traj.dimensions['atom']):
         rst_file.write_velocity(vels[it][0], vels[it][1], vels[it][2])

      # Now write the box information if it's present
      if 'cell_lengths' in traj.variables.keys():
         a = traj.variables['cell_lengths'][idx][0]
         b = traj.variables['cell_lengths'][idx][1]
         c = traj.variables['cell_lengths'][idx][2]
         alpha, beta, gamma = None, None, None
         if 'cell_angles' in traj.variables.keys():
            alpha = traj.variables['cell_angles'][idx][0]
            beta = traj.variables['cell_angles'][idx][1]
            gamma = traj.variables['cell_angles'][idx][2]
         rst_file.write_box_info(a, b, c, alpha, beta, gamma)
      
      # Now we're done with our restart file -- close it
      rst_file.close()

      print 'Done writing restart file %s.%d' % (opt.restrt, idx+1)
      

#~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+~+#

if __name__ == '__main__': main()
