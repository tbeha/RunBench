# -*- coding: utf-8 -*-
"""
Created on Fri Feb 12 08:22:56 2016

@author: thomasb
"""

import argparse
import os 
import re
import time
import csv
import xml.etree.ElementTree as ET
from pylab import *
from dataAnalyzeClass import *

DEBUG = False

disk = []
path='.'

##################################
# function readbenchXML          
#
# input parameters:
#    filename: benchmark init file
#
# output parameters:
#   test:  rname, rpath, desc
#   phase: warmup, measure, sample, cooldown, rest
#   load:  [access,rwstart,rwend,rwstep,rspmax,size,cachehits,offset],[]
#   host:  [name,disk],[]
#
###################################
def readInit(filename):
       
    phase = [] 
    load = []  
    host = []
    test = []
    desc = []
    access='random'
    rwstart='0'
    rwend='100'
    rwstep='10'
    rspmax='20'
    size='8192'
    cachehits='0'
    offset='[0.0,1.0]'
    qstep='1'    
    
    tree = ET.parse(filename)
    for el in iter(tree.find('Runinfo')):
        if el.tag == "name":
            rname = el.text
        elif el.tag == "path":
            rpath = el.text
        elif el.tag == "description":
            desc = el.text
        else:
            print("XML error - wrong Run tag: ",el.tag)
            continue
    test = [rname, rpath, desc]
    for el in iter(tree.find('Phase')):
        if el.tag == "warmup":
            warmup = el.text
        elif el.tag == "measure":
            measure = el.text
        elif el.tag == "sample":
            sample = el.text
        elif el.tag == "cooldown":
            cooldown = el.text
        elif el.tag == "rest":
            rest = el.text
        else:
            print ("XML error - wrong Phase tag: ",el.tag)
            continue
    phase = [warmup,measure,sample,cooldown,rest]
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
            elif sel.tag == "rspmax":
                rspmax = sel.text
            elif sel.tag == "size":
                size = sel.text
            elif sel.tag == "cachehits":
                cachehits = sel.text
            elif sel.tag == "offset":
                offset = sel.text
            elif sel.tag == "qstep":
                qstep = sel.text
            else:
                print ("XML error - wrong Load tag: ",sel.tag)
            continue
        load.append([access,rwstart,rwend,rwstep,rspmax,size,cachehits,offset,qstep])               
    for el in iter(tree.findall('Host')):
        for sel in iter(el):
            if sel.tag == "name":
                name = sel.text
            elif sel.tag == "disk":
                disk = sel.text
 #                      elif sel.tag == "direct":
 #                          direct = sel.text
 #                      elif sel.tag == "async":
 #                          async = sel.text
 #                      elif sel.tag == "delay":
 #                          delay = sel.text
            else:
                print ("XML error - wrong Host tag: ",sel.tag)
                continue
        host.append([name,disk])       
#                break
    return(test,phase,load,host)
### end readInit


###################################
# createfig
#
# Input:
#   csvfile: csvfile name
#   load:  [access,rwstart,rwend,rwstep,rspmax,size,cachehits,offset]
#
# Output:
#  
###################################
def createfig (dirname, load):
    
    d = dataAnalyze()
 #   d.readData(dirname)
    searchpattern=[]        
    readstart = int(load[1])
    readstep = int(load[3])
    readend = int(load[2]) + readstep
    iosize = str(int((int(load[5])/1024)))+'k'      
    figure() 
    i = 0
    access = str(load[0]).strip(' ')
    for j in range(readstart, readend, readstep):
        searchpattern.append = [[10,iosize],[11,load[0]],[12,j],[6, 'GrandTotal']]
        if access == 'random':
            d.xyplot(2,4,j,'o-',i)
        else:
            d.xyplot(3,4,j,'o-',i)
        i += 1
    header=iosize+' '+access
    title(header)
    if access == 'random':
        xlabel('Throughput [IOPS]')
    else:
        xlabel('Data Rate [MBps]')
    ylabel('Response Time [ms]')
    grid()
    legend(loc=0,ncol=3,mode="expand")    
    figname = dirname +"\\"+iosize+access+".png"
    savefig(figname)
    return (0)
# end createfig  



##########################################################################################################
#  Main
##########################################################################################################

# Read the benchmark.init file 

parser = argparse.ArgumentParser(prog='RunBenchmark.py',usage='python RunBenchmark.py -i initfile -m simulation/run')
parser.add_argument('-i')
parser.add_argument('-s')
initfile='3nodeVSAdl360-AO.xml'   
print (initfile)   
testrun, phase,load, hosts = readInit(initfile)
print(phase, load, hosts)
path = str(testrun[1]).strip(' ')
t = time.localtime()
tag=str(t[1])+str(t[2])+str(t[0])
dirname="\\3ndl360ao\\dl360-AO-run01.2112016"
#command='mkdir '+dirname
#os.system(command)
#command = 'copy '+initfile+' '+dirname
#os.system(command)

csvfile=dirname+"\\dl360-AO-run01.2112016.csv"
header=[['run #','sample','iops','mbps','rt','rtmax','host','disk','qdepth','population','iosize','access','reads%','runname','cachehits%','offset','targetsize','date','phase']]
#writecsv(header, csvfile)           

for h in iter(hosts):
    disk.append( h[0].strip(' ')+"@"+h[1].strip(' '))

for l in iter(load):   
    """ Get the load parameters """
    readstart = int(l[1])
    readstep = int(l[3])
    readend = int(l[2]) + readstep      
 #   for j in range(readstart, readend, readstep):
 #       """ Start applying the load to the disks one by one and then move on to increase the qdepth """        
 #       """ Create unique output filename: dp[iosize][access][timestamp].dp """        
 #       t = time.localtime()
 #       if int(l[5]) == 8192:
 #           ios="8k"
 #       elif int(l[5]) == 262144:
 #           ios="256k"
 #       else:
 #           ios=str(l[5])
 #       if str(l[0]).strip(' ') == 'random':
 #           acc='r'
 #       else:
 #           acc='s'
 #       dpoutput = "dp"+ios+acc+str(j)+"."
 #       dpoutput += str(t[1])+str(t[2])+str(t[0])+str(t[3])+str(t[4])+str(t[5])
 #       dpoutput += ".dp"
 #                         
 #       payload = [l[0],j,l[5],l[6],l[7]]  #  access, reads, size in k, cachehits, offset
 #       i = 0
 #       qdepth = 1
 #       target = [] 
 #       for k in range(len(disk)):
 #           target.append(disk[k])
 #           #result = runbench(i,1, phase, payload, target, path, dirname, dpoutput, csvfile,testrun[2],runmode)
 #           i += 1
 #       qdepth = 2          
    """ Create the graph at the end of a load run """
    createfig(dirname,l)