# -*- coding: utf-8 -*-
"""
Created on Fri Feb 13 05:47:47 2015

@author: BEHAT
"""

import os
import xml.etree.ElementTree as ET
import re
import csv
import sys
from pylab import *

class dataAnalyze:
    """
    class dataAnalyze
    routines for the data crunching on the vesper csv output files
    """
    
    path = '.'      # search path
    runinfo = []    # run list with info
    data = []       # csv-file data
    subset = []     # subset of the csv-file data based on the latest searchpatten
    
    
    def getRunList (self, path):
        """
        populates the runinfo[]
        each runinfo entry is composed of:
            runname
            description
            [[access,rwstart,rwend,rwstep,size,cachehists,offset],...]
            [[hostname,disk],...]
            rootdir
            filename
        """
        self.path = path
        for root, dirs, files in os.walk(self.path):
            for filename in files:
                if re.search(r'.xml$',filename):
                    cur_file = os.path.join(root,filename)
                    tree = ET.parse(cur_file)
                    if tree.find('Runinfo'):  # check that you really have a Runinfo xml file
                        host=[]
                        load=[]
                        for el in iter(tree.find('Runinfo')):
                            if el.tag == "name":
                                runname = el.text
                            elif el.tag == "description":
                                desc = el.text
                        for el in iter(tree.findall('Load')):
                            for sel in iter(el):
                                if sel.tag == "access":
                                    access = sel.text
                                elif sel.tag == "rwstart":
                                    rwstart = sel.text
                                elif sel.tag == "rwend":
                                    rwend = sel.text
                                elif sel.tag == "rwstep":
                                    rwstep = sel.text
                                elif sel.tag == "size":
                                    size = sel.text
                                elif sel.tag == "cachehits":
                                    cachehits = sel.text
                                elif sel.tag == "offset":
                                    offset = sel.text
                            load.append([access,rwstart,rwend,rwstep,size,cachehits,offset])        
                        for el in iter(tree.findall('Host')):
                            for sel in iter(el):
                                if sel.tag == "name":
                                    name = sel.text
                                elif sel.tag == "disk":
                                    disk = sel.text
                                    host.append([name,disk])
                        runX=[runname,desc,load,host,root,filename]
                        self.runinfo.append(runX)        
    """ End createRunList() ------------------------------------------------------------------"""
                         
    def readData(self, inputdirectory):
        """
        reads a complete csv-file into data[]
        data[] structure:
            0 - run#
            1 - sample
            2 - iops
            3 - mbps
            4 - rt
            5 - rtmax
            6 - host
            7 - disk
            8 - qdepth 
            9 - population
            10 - iosize (8k, 256k, ...)
            11 - access (random, segmented)
            12 - reads% (0%, 10%, ..., 100%)
            13 - runname
            14 - cachehits (0%,...)
            15 - offset [0,1.0]
            16 - targetsize [xxxGB]
            17 - data
            18 - phase
        """
        self.data=[]
        dp = inputdirectory.split('\\')
        inputfile=inputdirectory+'\\'+dp[(len(dp)-1)]+'.csv'
        with open(inputfile,'r', newline='') as csvf:
            print ('opened:',inputfile)
            datareader = csv.reader(csvf, dialect='excel', delimiter=',')
            for row in datareader:
                self.data.append(row)
            csvf.close()
    """ End readData() -----------------------------------------------------------------------"""

    def searchData (self, searchpattern):
        """"
        populates the subset based on the searchpattern
        seachpattern = [[index:pattern],...]
        """
        self.subset=[]
        for row in self.data:
            hit = True
            for search in searchpattern:
                index = search[0]
                pattern = search[1]
                if row[index] != pattern:
                    hit = False
                    break
            if hit == True:
                self.subset.append(row)
        

    """ End searchData() ---------------------------------------------------------------------"""
        
    def xyplot (self, xindex, yindex, lbl, style, color):
        """
        uses the subset data and plots subset[xindex] vs. subset[yindex]
        """
        print ("xyplot")
        linecolor=((1,0,0),(1.0,0.6,0),(1,1,0),(0,0.5,0),(0,0,1),(0.8,0.2,0.5),(0.5,1,0.2),(0,0.8,1),(0.4,0,0.8),(0.6,1,0.6),(0.12,0.12,0.3))
        x=[]
        y=[]
        for row in self.subset:
            x.append(row[xindex])
            y.append(row[yindex])
        plot(x,y,style,label=lbl,linewidth=2,color=linecolor[color]) 
    """ --- end xyplot() ---- """
       
    def histo (self, searchpattern, runname):
        """
        creates a histogramm of subset(xindex)
        """
        histodata=[]
        iops=[]
        N = 20
        figure()        
        for s in searchpattern:
            lpattern=[]
            for i, d in enumerate(s):
                if i > 0:
                    lpattern.append(d)
            self.searchData(lpattern)
            for row in self.subset:
                if row[1] == 'avg':
                    for io in iops:
                        delta = float(io) - float(row[3])
                        histodata.append(delta)
                    iops=[]
                else:
                    iops.append(row[3])                   
        # end search the data
        # now it is time to start creating the histogram
        min = histodata[0]
        max = histodata[0]
        for h in histodata:
            if h < min:
                min = h
            if h > max:
                max = h
        steps=(max-min)/N        
        prob, bins, patches = hist(histodata,arange(min,max,steps),align='left')
        xlabel('IOPS - AVG(IOPS)')
        ylabel('Counts')
        header=lpattern[2][1]+' '+lpattern[3][1]+' '+runname
        title(header)
        grid()
        show()        
        
    """ --- end histo ---- """                

    def writecsv (self, output, csvfile):
        """
        writes the output into a csvfile
        """
        with open(csvfile,'a', newline='') as csvf:
            datawriter = csv.writer(csvf, dialect='excel', delimiter=',')
            for row in output:
                datawriter.writerow(row)
            csvf.close()          
    """ --- end writecsv --- """
                    