#! /usr/bin/env python
# -*- coding: utf-8 -*-

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
#import pandas as pd
import os
#import commands
import subprocess
import json
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
                        help='config file for iperf3 test')

    parser.add_argument('-N', '--testname',
                        required=True,
                        action='store',
                        help='name for the iperf3 test, not to be unique')

    parser.add_argument('-i', '--interval',
                        required=False,
                        action='store',
                        help='second for periodic bandwidth report, defaulty no report')

    parser.add_argument('-b', '--bandwidth',
                        required=False,
                        action='store',
                        help='target bandwidth in bps, default 1 Mbit/sec for UDP, unlimited for TCP')

    parser.add_argument('-M', '--mss',
                        required=False,
                        action='store',
                        help='TCP maximum segmnet size (MTU - 40), default 1460 bytes')

    parser.add_argument('-P', '--parallel',
                        required=False,
                        action='store',
                        help='number of parallel client streams to run, default 1 stream')

    parser.add_argument('-t', '--time',
                        required=False,
                        default='10',
                        action='store',
                        help='time in seconds to transmit for, default 10 secs')

    parser.add_argument('-u', '--udp',
                        required=False,
                        action='store_true',
                        help='use UDP rather than TCP')

    parser.add_argument('--getserveroutput',
                        required=False,
                        action='store_true',
                        help='get iperf3 test results from servers')

    parser.add_argument('--getesxtop',
                        required=False,
                        action='store_true',
                        help='get esxtop measurement results from hosts')

    args = parser.parse_args()
    return args

def get_option(args):
    print "[Test parameters per Peers]"
    options = " -C " + args.configfile + " -N " + args.testname + " -J -s "
    if args.udp:
        options = options + " -u "
        print "| Protocol: UDP",
    else:
        print "| Protocol: TCP",
    if args.bandwidth:
        options = options + " -b " + args.bandwidth
        print "| Bandwidth(bps): " + args.bandwidth,
    else:
        if args.udp:
          print "| Bandwidth(bps): 1M",
        else:
          print "| Unlimitted Bandwidth",
    if args.mss:
        options = options + " -M " + args.mss
        print "| MSS(byte): " + args.mss,
    else:
        print "| MSS(byte): 1460",
    if args.parallel:
        options = options + " -P " + args.parallel
        print "| Streams: " + args.parallel,
    else:
        print "| Streams: 1",
    if args.interval:
        options = options + " -i " + args.interval
        print "| Interval(s): " + args.interval,
    else:
        print "| Interval(s): 1",
    if args.time:
        options = options + " -t " + args.time
        print "| Time(s): " + args.time,
    else:
        print "| Time(s): 10",
    if args.getesxtop:
        options = options + " -E "
        print "| Capture ESXTOP",
    if args.getserveroutput:
        options = options + " -G "
        print "| Use Server side data"
    else:
        print "| Use Client side data"

    return options

def init_plt_iperf3():
    plt.figure(num=None, figsize=(20, 6), dpi=60, facecolor='w', edgecolor='k')
    plt.rcParams["font.size"] = 15
    plt.rcParams["xtick.labelsize"] = 12
    plt.rcParams["ytick.labelsize"] = 12
    plt.rcParams["legend.fontsize"] = 12
    plt.grid()
    plt.axhline(y=0)
    plt.xlabel("Interval(s)")
    plt.ylabel(u"Throughput(Gbps)")
    plt.gca().yaxis.set_major_formatter(FixedOrderFormatter(9, useOffset=False))
    plt.gca().get_xaxis().set_major_locator(ticker.MaxNLocator(integer=True))
    # plot.hold(True)

def init_plt_esxtop():
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

    cmd = "../scripts/run_iperf3_peer.bash "
    cmd_options = get_option(args)

    print 'Testing, wait {} seconds... '.format(args.time),
    dirname = str(subprocess.check_output( cmd+cmd_options, shell=True, universal_newlines=True )).replace('\n','')
    print 'done'

    json_files = glob.glob(dirname + "/*cl*.json")
    print "[Test Result]"
    print "| Number of peers: " + str(len(json_files))

    csv_files = glob.glob(dirname + "/*esxtop*.csv")
    print "[Test Result]"
    print "| Number of hosts: " + str(len(csv_files))
    print ""

    x={}
    y={}
    t=np.zeros(int(args.time))
    i=0

    # process iperf3 JSON files
    init_plt_iperf3()
    
    for file in json_files:
        print(file)
        f = open(file, 'r')
        perf_dict = json.load(f)

        if args.udp:
            print "| Avg Bandwidth(Gbps): " + str(perf_dict["end"]["sum"]["bits_per_second"] / 1000000000), 
            print "| Jitter(ms): " + str(perf_dict["end"]["sum"]["jitter_ms"]), 
            print "| Lost Packets: " + str(perf_dict["end"]["sum"]["lost_packets"]),
            print "| Lost %: " + str(perf_dict["end"]["sum"]["lost_percent"])
            print "| Sender CPU%: " + str(perf_dict["end"]["cpu_utilization_percent"]["host_total"]), 
            print "| Receiver CPU%: " + str(perf_dict["end"]["cpu_utilization_percent"]["remote_total"])
        else:
            print "| Avg Bandwidth(Gbps): " + str(perf_dict["end"]["sum_received"]["bits_per_second"] / 1000000000),
            print "| Retransmits: " + str(perf_dict["end"]["sum_sent"]["retransmits"]) 
            print "| Sender CPU%: " + str(perf_dict["end"]["cpu_utilization_percent"]["host_total"]),
            print "| Receiver CPU%: " + str(perf_dict["end"]["cpu_utilization_percent"]["remote_total"])

        x[i] = np.array(range(len(perf_dict["intervals"])))
        y[i] = np.array([])
        
        for p in perf_dict["intervals"]:
            y[i] = np.append(y[i], p["sum"]["bits_per_second"])
        
        plt.plot(x[i], y[i], color[i],marker="o",markersize=3)
        t=t+y[i]

        i=i+1
        
    plt.plot(x[0], t, "k", marker="X", markersize=5, linewidth=2)
    plt.show()

    # process esxtop CSV files
    for file in csv_files:
        init_plt_esxtop()

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
