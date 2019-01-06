#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
#import pandas as pd
import os
#import commands
import subprocess
#import json
import csv
import argparse
import glob
import re

class rdict(dict):
    def __getitem__(self, key):
        try:
            return super(rdict, self).__getitem__(key)
        except:
            try:
                ret=[]
                for i in self.keys():
                    m= re.match("^"+key+"$",i)
                    if m:ret.append( super(rdict, self).__getitem__(m.group(0)) )
            except:raise(KeyError(key))
        return ret

    def __getkey__(self, key):
        try:
            return super(rdict, self).__getkey__(key)
        except:
            try:
                ret=[]
                for i in self.keys():
                    m= re.match("^"+key+"$",i)
                    if m:ret.append( i )
            except:raise(KeyError(key))
        return ret

    def __getdict__(self, key):
        try:
            return super(rdict, self).__getdict__(key)
        except:
            try:
                ret=[]
                for i in self.keys():
                    m= re.match("^"+key+"$",i)
                    if m:ret.append( {i:super(rdict, self).__getitem__(m.group(0))} )
            except:raise(KeyError(key))
        return ret

class FixedOrderFormatter(ticker.ScalarFormatter):
    def __init__(self, order_of_mag=0, useOffset=True, useMathText=True):
        self._order_of_mag = order_of_mag
        ticker.ScalarFormatter.__init__(self, useOffset=useOffset, 
                                 useMathText=useMathText)
    def _set_orderOfMagnitude(self, range):
        self.orderOfMagnitude = self._order_of_mag

def get_args():
    """Get command line args from the user.
    """
    parser = argparse.ArgumentParser(
        description='Standard Arguments for talking to iperf programs')

    parser.add_argument('-C', '--configfile',
                        required=True,
                        action='store',
                        help='config file for apache bench test')

    parser.add_argument('-N', '--testname',
                        required=True,
                        action='store',
                        help='name for the apache bench test, not to be unique')

    parser.add_argument('-n', '--number',
                        required=False,
                        action='store',
                        help='number of total requests to perform per client')

    parser.add_argument('-c', '--concurrency',
                        required=False,
                        action='store',
                        help='number of multiple requests to make at a time per client')

    parser.add_argument('-t', '--timelimit',
                        required=False,
                        action='store',
                        help='Max time (sec) to spend on benchmarking. This implies -n 50000')

    args = parser.parse_args()
    return args

def get_option(args):
    print "[Test parameters per Client]"
    options = " -C " + args.configfile + " -N " + args.testname + " -s "
    if args.timelimit:
        args.number = 50000
        options = options + " -t " + args.timelimit + " -n " + args.number
        print "| Time Limit(s): " + args.timelimit,
        print "| Total Requests: " + args.number,
    else:
        print "| Time Limit(s): 10",
        if args.number:
            options = options + " -n " + args.number
            print "| Total Requests: " + args.number,
        else:
            print "| Total Requests: 1",
    if args.concurrency:
        options = options + " -c " + args.concurrency
        print "| Concurrency: " + args.concurrency,
    else:
        print "| Concurrency: 1",

    print ""
    return options

def init_plt():
    plt.figure(num=None, figsize=(20, 6), dpi=60, facecolor='w', edgecolor='k')
    plt.rcParams["font.size"] = 15
    plt.rcParams["xtick.labelsize"] = 12
    plt.rcParams["ytick.labelsize"] = 12
    plt.rcParams["legend.fontsize"] = 12
    plt.grid()
    plt.axhline(y=0)
    plt.xlabel("Time(s)")
    plt.ylabel("Physical CPU(%)")
    plt.gca().yaxis.set_major_formatter(FixedOrderFormatter(0, useOffset=False))
    plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))

color=['r','b','g','y','p','r','b','g','y','p']
key_util = ".*Physical Cpu\(_Total\)\\\\\% Util Time"
key_core = ".*Physical Cpu\(_Total\)\\\\\% Core Util Time"
key_proc = ".*Physical Cpu\(_Total\)\\\\\% Processor Time"
    
#'\\\\DL360-ESX1\\Physical Cpu(_Total)\\% Util Time': '1.21'
#'\\\\DL360-ESX1\\Physical Cpu(_Total)\\% Core Util Time': '2.28'
#'\\\\DL360-ESX1\\Physical Cpu Load\\Cpu Load (15 Minute Avg)': '0.81'
#'\\\\DL360-ESX1\\Physical Cpu Load\\Cpu Load (5 Minute Avg)': '0.81'
#'\\\\DL360-ESX1\\Physical Cpu Load\\Cpu Load (1 Minute Avg)': '0.81'
#'(PDH-CSV 4.0) (UTC)(0)': '05/15/2018 02:13:06'

def main():
    
    args = get_args()

    cmd = "../scripts/run_abench_cl.bash "
    cmd_options = get_option(args)

    print 'Testing, wait until test complete... ',
    dirname = str(subprocess.check_output( cmd+cmd_options, shell=True, universal_newlines=True )).replace('\n','')
    print 'done'

    result_files = glob.glob(dirname + "/*-ab-*.result")
    print "[Test Result]"
    print "| Number of clients: " + str(len(result_files))

    csv_files = glob.glob(dirname + "/*esxtop*.csv")
    print "[Test Result]"
    print "| Number of hosts: " + str(len(csv_files))
    print ""

    for file in result_files:
        print(file)
        with open(file) as f:
            for line in f:
#                m = re.match("^Document Length: *([0-9]* bytes)$", line)
                print line.rstrip("\n")

#    x={}
#    y_util={}
#    y_core={}
#    y_proc={}

    for file in csv_files:
        init_plt()

        print(file)
        print("| Red - CPU Total Util | Blue - CPU Total Core Util | Green - CPU Total Proc Time |")
        with open(file) as cf:
            reader = csv.DictReader(cf, delimiter=",")
            perf_dict = []
            for row in reader:
                perf_dict.append(row)

        # X-scale must be coordinated as ESXTOP will be executed per 5 secs.
        x = (np.array(range(len(perf_dict)))+1)*5

        y_util = np.array([])
        y_core = np.array([])
        y_proc = np.array([])
        
        for p in perf_dict:
            rd = rdict(p)
            y_util = np.append(y_util, float(rd[key_util][0]))
            y_core = np.append(y_core, float(rd[key_core][0]))
            y_proc = np.append(y_proc, float(rd[key_proc][0]))
        
#        print x, y_util, y_core, y_proc
        plt.plot(x, y_util, "r", marker="o",markersize=3)
        plt.plot(x, y_core, "b", marker="o",markersize=3)
        plt.plot(x, y_proc, "g", marker="o",markersize=3)
        plt.show()

# Start program
if __name__ == "__main__":
    main()
