# -*- coding: utf-8 -*-
"""
Vesper Benchmark Toolset 

@author: Thomas Beha
@version: 1.0
@date:  11/27/2014
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
# function analyzeOutput (filename)
#   Input:
#     filename
#     csvfilename
#   Output:
#     responsetime
##################################
def analyzeOutput(filename, csvfilename, run):
    """" Analyzing the output.dp file """
    # key: host:diskname or GrandTotal
    # result[key]=[sample,iops,mbps,rt,rtmax]
    # target[key]=[host, diskname, qdepth, population, iosize, access, runname, run#, cachehits, offset, targetsize, date, phase]
    output=[]
    tmpoutput=[]
    targets={}    
    phase={}
    qdepth='1'
    iosize='8k'
    access='random'
    offset='[0.0,1.0]'
    reads='100%'
    cachehits='0%'
    disksize='1 GB'
    responsetime='-1'
    
    # flags = [workload, targetsizes, result, phase, target]    
    flags=['False','False','False', 'False', 'False']
    
    data = open('output.dp','r').readlines()
    #
    # get the header information of the benchmark
    #
    # run=0
    for i, line in enumerate(data):
        if re.search('HP Company Confidential',line):
            tmp = line.split()
            date = tmp[4]+' '+tmp[5]
        if re.search('Workload:',line):
            flags[0] = True
        elif re.search('Host\[',line):
            host = (line.split())[2]
        elif re.search('Phase\[',line):
            flags[3]=True
            tmp = line.split()
            for k in range(len(tmp)):
                if re.search('warmup',tmp[k]):
                    phase['warmup'] = tmp[k+2]
                elif re.search('measure',tmp[k]):
                    phase['measure'] = tmp[k+2]
                elif re.search('sample',tmp[k]):
                    phase['sample'] = tmp[k+2]
                elif re.search('cooldown',tmp[k]):    
                    phase['cooldown'] = tmp[k+2]
                elif re.search('rest',tmp[k]):
                    phase['rest'] = tmp[k+2]
                else:
                    continue
        elif re.search('Target\[',line):
            flags[4]=True
            flags[3]=False
            disk = (line.split())[2]
            disk = disk.strip("\\\\.\\")  
            key=host+'-'+disk
        elif re.search('Workload-end',line):
            flags[0] = False
        elif re.search('Target sizes:',line):
            flags[1] = True
        elif re.search('Phase 1 execute',line):
            flags[2]=True
        elif re.search('Phase 1 complete',line):
            flags[2]=False
            # run += 1
            writecsv(output, csvfilename)
            output=[]
            targets={}
            fname=dirname+"\\"+dpoutput
            f = open(fname,'a')
            for k in range(len(data)):
                f.write(data[k])
            f.close()
        else:         
            if flags[3] == True: # Phase information
                tmp = line.split()
                for k in range(len(tmp)):
                    if re.search('warmup',tmp[k]):
                        phase['warmup'] = tmp[k+2]
                    elif re.search('measure',tmp[k]):
                        phase['measure'] = tmp[k+2]
                    elif re.search('sample',tmp[k]):
                        phase['sample'] = tmp[k+2]
                    elif re.search('cooldown',tmp[k]):    
                        phase['cooldown'] = tmp[k+2]
                    elif re.search('rest',tmp[k]):
                        phase['rest'] = tmp[k+2]
                    else:
                        continue    
            elif flags[4] == True: # Target information
                tmp = line.split()
                if re.search('qdepth',line):
                    qdepth=(line.split())[2]
                elif re.search('access',line):
                    access=(line.split())[2]
                elif re.search('offset',line):
                    offset=(line.split())[2]+','+(line.split())[3]
                elif re.search('reads',line):
                    reads=(line.split())[2]
                elif re.search('blocksize',line):
                    iosize=str(int(int((line.split())[2])/1024))+'k'
                elif re.search('cache hits',line):
                    cachehits=(line.split())[3]
                elif re.search('Target-end',line):
                    flags[4]=False
                    targets[key]=[host,disk,qdepth,1,iosize,access,reads,filename,cachehits,offset,0,date,phase]
                elif re.search('Host-end',line):
                    print ("host-end - Workload:",flags)
                else:
                    continue
            elif flags[1] == True: # Targetsize information
                if re.search('Host =',line):
                   host = line.split()[2]
                elif re.search('Target =',line):
                    tmp = line.split()
                    disk = tmp[2]
                    disk = disk.strip("\\\\.\\")
                    key=host+'-'+disk
                    disksize = str(int(int(tmp[4])/(1024*1024*1024)))+' GB'
                    (targets[key])[10]=disksize
                elif re.search('Target sizes-end',line):
                    flags[1] = False
                    n = len(targets)
                    tt = []
                    for k in targets[key]:
                        tt.append(k)
                    tt[3]=n
                    tt[0]='GrandTotal'
                    tt[1] = targets.keys()
                    targets['GrandTotal']=tt
            elif flags[2] == True: # results
                tmp = line.split()
                if re.search('Host',line) and len(tmp) < 3:
                    host = (tmp[1]).strip(':')
                elif re.search('PHYSICALDRIVE',line):
                    tmp=line.strip()
                    disk=tmp.strip("\\\\.\\")                   
                    key=host+'-'+disk
                    phase = (targets[key])[12]
                    samples = int(phase['measure'])/int(phase['sample'])
                    for k in range(int(i+1),int(i+samples+1)):
                        tmpoutput=[run]+data[k].split()+targets[key]
                        population = int(tmpoutput[8])  # get the population = qdepth * number of disks
                        population *= int(tmpoutput[9])
                        tmpoutput[9] = population
                        output.append(tmpoutput)
                    tmpoutput = [run,'avg'] + data[int(i+samples+2)].split() + targets[key]
                    tmpoutput[9] = int(tmpoutput[9])*int(tmpoutput[8])
                    output.append(tmpoutput)
                    tmpoutput=[]
                elif re.search('/dev/sd',line):
                    disk=line.strip()
                    key=host+'-'+disk
                    phase = (targets[key])[12]
                    samples = int(phase['measure'])/int(phase['sample'])
                    for k in range(int(i+1),int(i+samples+1)):
                        tmpoutput=[run]+data[k].split()+targets[key]
                        population = int(tmpoutput[8])  # get the population = qdepth * number of disks
                        population *= int(tmpoutput[9])
                        tmpoutput[9] = population
                        output.append(tmpoutput)
                    tmpoutput = [run,'avg'] + data[int(i+samples+2)].split() + targets[key]
                    tmpoutput[9] = int(tmpoutput[9])*int(tmpoutput[8])
                    output.append(tmpoutput)
                    tmpoutput=[]                    
                elif re.search(re.compile("Grand Total"),line):
                    key = 'GrandTotal'
                    for k in range(int(i+3),int(i+samples+3)):
                        tmpoutput=[run]+data[k].split()+targets[key]
                        tmpoutput[9] = int(tmpoutput[9]) * int(tmpoutput[8])
                        output.append(tmpoutput)
                    tmpoutput = [run,'avg'] + data[int(i+samples+4)].split() + targets[key]
                    responsetime=tmpoutput[4]
                    tmpoutput[9] = int(tmpoutput[9]) * int(tmpoutput[8])
                    output.append(tmpoutput)
                    tmpoutput=[]
                else:
                    continue
            else:
                continue        
        
    return(responsetime)

### End analyzeOutput


###################################
#  function writecsv(output, csvfile) 
###################################
def writecsv (output, csvfile):
    
    # csvfile - columns:
    # run#, sample, iops, mbps, rt, rtmax, host, disk, qdepth, population, iosize, access, reads%, cachehits%, offset, targetsize, phase, date        
   # print(output)
    with open(csvfile,'a', newline='') as csvf:
        datawriter = csv.writer(csvf, dialect='excel', delimiter=',')
        for row in output:
            datawriter.writerow(row)
            if row[1] == 'avg' and row[6] == 'GrandTotal':
                print (row[1],row[2],'IOPS',row[3],'MBps',row[4],'ms')
        csvf.close()          
    return(0)
# end writecsv

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
    d.readData(dirname)
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

##########################################################
#  runbench
#
#  Input:
#   iteration: phase number
#   qdepth: current vesper qdepth
#   phase=[warmup, measure, sample, cooldown, rest]
#   load:  [access,rwstart,rwend,rwstep,rspmax,size,cachehits,offset]
#   disks: list of current targets for this run
#   searchpath: root directory where the vesper output resides 
#   dirname: output directory 
#   outputfile: output filename, dp[iosize in k][reads][access][date].dp
#   csvfile: csvfile name
#   description: benchmark description as it is given in the init file
#
#  Output:
#    responsetime: return the Grand Total avg. responsetime
#
##########################################################
def runbench(iteration, qdepth, phase, load, disks, searchpath, dirname, outputfile, csvfile, description,runmode):
    
    """ Create the vesper file """
    header = "warmup= "+ phase[0] +"\n"
    header += "measure= "+ phase[1] +"\n"
    header +="sample= " + phase[2] +"\n"
    header +="cooldown= " + phase[3] +"\n"
    header += "rest= " + phase[4] +"\n"
    header += "update = 0 \n"
    header += "verbose = true \n"
    header += "pretty = true \n"
    header += "histogram = false \n"
    header += "align = 0 \n"
    header += "delay = 0 \n"
    header += "accelerator = 1 \n"
    header += "cachehits =" + load[3] + "\n"
    header += "rwstats = false \n"
    header += "prefill = false \n \n" 
    header += "!phase blocksize= "
    header += load[2] 
    header += " size=1 access= " + load[0]
    header += " qdepth=" + str(qdepth)
    header += " reads=" + str(load[1])
    header += " offset=" + load[4] + "\n"
    f = open("vesper.load","w")
    f.write(header)
    for d in iter(disks):
        f.write(d) 
        f.write("\n")
    f.close()
    
    """ Start vesper """   
    if runmode == 'simulation':
        print('Simulation')
    else:
        os.system('vesper vesper.load > output.dp')        
    responsetime = analyzeOutput(outputfile, csvfile, iteration)
    return(responsetime) # return the Grand Total avg. responsetime for  
# End def runbench()

##########################################################################################################
#  Main
##########################################################################################################

# Read the benchmark.init file 

parser = argparse.ArgumentParser(prog='RunBenchmark.py',usage='python RunBenchmark.py -i initfile -m simulation/run')
parser.add_argument('-i')
parser.add_argument('-s')
if DEBUG:
    initfile='kvmvsarun1.xml'
    runmode=''    
else:    
    initfile=vars(parser.parse_args())['i']
    runmode=vars(parser.parse_args())['s']
 
print (initfile)   
testrun, phase,load, hosts = readInit(initfile)

##############################################################
# Prepare Output directory and result csv file
##############################################################
path = str(testrun[1]).strip(' ')
t = time.localtime()
tag=str(t[1])+str(t[2])+str(t[0])
dirname=path+"\\"+str(testrun[0]).strip(' ')+'.'+tag
command='mkdir '+dirname
os.system(command)
command = 'copy '+initfile+' '+dirname
os.system(command)

csvfile=dirname+"\\"+str(testrun[0]).strip(' ')+'.'+tag+".csv"
header=[['run #','sample','iops','mbps','rt','rtmax','host','disk','qdepth','population','iosize','access','reads%','runname','cachehits%','offset','targetsize','date','phase']]
writecsv(header, csvfile)           

##############################################################
# create target list
##############################################################
for h in iter(hosts):
    disk.append( h[0].strip(' ')+"@"+h[1].strip(' '))

#############################################################
# Go through the load list
#############################################################
for l in iter(load):   
    """ Get the load parameters """
    readstart = int(l[1])
    readstep = int(l[3])
    readend = int(l[2]) + readstep      
    for j in range(readstart, readend, readstep):
        """ Start applying the load to the disks one by one and then move on to increase the qdepth """        
        """ Create unique output filename: dp[iosize][access][timestamp].dp """        
        t = time.localtime()
        if int(l[5]) == 8192:
            ios="8k"
        elif int(l[5]) == 262144:
            ios="256k"
        else:
            ios=str(l[5])
        if str(l[0]).strip(' ') == 'random':
            acc='r'
        else:
            acc='s'
        dpoutput = "dp"+ios+acc+str(j)+"."
        dpoutput += str(t[1])+str(t[2])+str(t[0])+str(t[3])+str(t[4])+str(t[5])
        dpoutput += ".dp"
                          
        payload = [l[0],j,l[5],l[6],l[7]]  #  access, reads, size in k, cachehits, offset
        i = 0
        qdepth = 1
        target = [] 
        for k in range(len(disk)):
            target.append(disk[k])
            result = runbench(i,1, phase, payload, target, path, dirname, dpoutput, csvfile,testrun[2],runmode)
            i += 1
        qdepth = 2          
        while float(result) < float(l[4]):
            result = runbench(i, qdepth,phase, payload, disk, path, dirname, dpoutput, csvfile,testrun[2],runmode)
            i +=1
            qdepth += int(l[8]) # qstep
    """ Create the graph at the end of a load run """
    createfig(dirname,l)