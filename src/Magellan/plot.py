# -*- coding: utf-8 -*-

"""
plot.py - plots data for magellan

Copyright (C) 2008 Tryggvi Björgvinsson <tryggvib@hi.is>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from pylab import *
import Magellan
from Magellan.calc import *

_default_thickness = '0.5'

def create_plot(dist, dist_anom, deep, anom, layer, faultrift, model, parameters):
    """
    Plot bathymetry profiles from distance, depth,
    anomalies, the magnetic layer and a model.
    Uses matplotlib to plot a nice graph.
    """

    thickness = eval(parameters.get('thickness', _default_thickness))
        
    fig = figure(figsize=(12,8))
    anomplot = fig.add_subplot(211)
    bathplot = fig.add_subplot(212,sharex=anomplot)
    
    anomplot.set_title('Anomalies')
    anomplot.set_ylabel('nT')
    anomplot.plot(dist_anom, anom, '#330099', label="Data")
    anomplot.plot(dist, model, '#FF9900', label="Model")
    bathplot.set_title('Bathymetry')
    bathplot.set_xlabel('km')
    bathplot.set_ylabel('km')
    stuff=[]
    for index in range(len(deep)):
	deep[index] = deep[index]*-1
	stuff.append(0)


    deepthick = map(lambda x: x-thickness, deep)
    f=open('blocks','w')

    for ((start,end),polarity,magnet) in layer:
        if polarity == 'n': fillcolor = 'b'
        else: fillcolor = 'w'

	# The next index above start
        index_lower = next_upper(dist,start)
        # The next index below end        
	index_upper = next_lower(dist,end)

	# Finding the excact depth at start and end
	y_start = get_depth(dist,deep,start)
        y_end = get_depth(dist,deep, end)
	y_start_lower = y_start-thickness
        y_end_lower = y_end-thickness

        if (index_lower == index_upper +1):
	    xs = [start,end]
	    lys = [y_start, y_end]
	    tys = [y_start_lower, y_end_lower] 
        else:
            xs = [start]+dist[index_lower:index_upper+1]+[end]
            lys = [y_start]+deep[index_lower:index_upper+1]+[y_end]
            tys = [y_start_lower]+ deepthick[index_lower:index_upper+1] + [y_end_lower]
	    
        x = concatenate( (xs, xs[::-1]) )
        y = concatenate( (lys, tys[::-1]) )
	m = []
	depth = []
	    
	if fillcolor == 'b':
	    for i in range(len(xs)):		
		m.append(xs[i])	    
		depth.append(lys[i])
	if fillcolor == 'w':
	    for i in range(len(xs)):
		m.append(xs[i])
	    	depth.append(-1*lys[i])
	    ## Producing a file called blocks which can be used to plot up in gmt
	    
	if (end >= dist_anom[0] and start <= dist_anom[-1]):
	    if fillcolor == 'b':
	        f.write("> -Gblack\n")
	        for i in range(len(x)):
	    	    f.write(str(x[i])+ " " + str(y[i]) + "\n")
	    else:
	        f.write("> -Gwhite\n")
	        for i in range(len(x)):
		    f.write(str(x[i])+ " " + str(y[i]) + "\n")
          
	bathplot.fill(x, y, facecolor=fillcolor)



        #if (index_lower != index_upper):
            #xs = dist[index_lower:index_upper+1]
            #lys = deep[index_lower:index_upper+1]
            #tys = deepthick[index_lower:index_upper+1]
	    
            #x = concatenate( (xs, xs[::-1]) )
            #y = concatenate( (lys, tys[::-1]) )
	    #m = []
	    #depth = []
	    
	    #if fillcolor == 'b':
		#for i in range(len(xs)):		
		    #m.append(xs[i])	    
		    #depth.append(lys[i])
	    #if fillcolor == 'w':
		#for i in range(len(xs)):
		    #m.append(xs[i])
	    	    #depth.append(-1*lys[i])
	    ## Producing a file called blocks which can be used to plot up in gmt
	    
	    #if (end >= dist_anom[0] and start <= dist_anom[-1]):
	    	#if fillcolor == 'b':
	            #f.write("> -Gblack\n")
	            #for i in range(len(x)):
	    	 	#f.write(str(x[i])+ " " + str(y[i]) + "\n")
	    	#else:
	            #f.write("> -Gwhite\n")
	            #for i in range(len(x)):
			#f.write(str(x[i])+ " " + str(y[i]) + "\n")
          
	    #bathplot.fill(x, y, facecolor=fillcolor)
    f.close()
    #Fix to get one entry per fault/rift in legend
    fault_plotted = False
    rift_plotted = False
    dx = 0.3
    for (position,fault,rift) in faultrift:
        if fault:
            anomplot.axvspan(position-dx,position+dx,
            		     facecolor='#339900',edgecolor='none')
            if fault_plotted:
                bathplot.axvspan(position-dx,position+dx,
            	    	         facecolor='#339900',edgecolor='none')
            else:
                bathplot.axvspan(position-dx,position+dx,
            	    	         facecolor='#339900',edgecolor='none',
            	    	         label="Pseudofault")
                fault_plotted = True
        if rift:
            anomplot.axvspan(position-dx,position+dx,
            		     facecolor='r',edgecolor='none')
            if rift_plotted:
                bathplot.axvspan(position-dx,position+dx,
            		         facecolor='r',edgecolor='none')
            else:
                bathplot.axvspan(position-dx,position+dx,
            		         facecolor='r',edgecolor='none',
            	    	         label="Failed rift")
            	rift_plotted = True

 
    bathplot.plot(dist, deep, linewidth=2)
    anomplot.plot(dist, stuff, linewidth=0.5)
    bathplot.set_xlim(min(dist_anom),max(dist_anom))
    bathplot.set_ylim(min(deepthick),0)
    #anomplot.set_ylim(-100,100)
    anomplot.legend()
    bathplot.legend()

    show()

