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
import argparse
import glob

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
        description='Standard Arguments for talking to vCenter')

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

    parser.add_argument('-t', '--time',
                        required=False,
                        action='store',
                        help='time in seconds to transmit for, default 10 secs')

    parser.add_argument('-u', '--udp',
                        required=False,
                        action='store_true',
                        help='use UDP rather than TCP')

    args = parser.parse_args()
    return args

def get_option(args):
    options = " -C " + args.configfile + " -N " + args.testname + " -J -s "
    if args.interval:
        options = options + " -i " + args.interval
    if args.bandwidth:
        options = options + " -b " + args.bandwidth
    if args.time:
        options = options + " -t " + args.time
    if args.udp:
        options = options + " -u "

    return options

def init_plt():
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
    
def main():
    
    args = get_args()

    cmd = "../scripts/run_iperf3_peer.bash "
    cmd_options = get_option(args)

    dirname = str(subprocess.check_output( cmd+cmd_options, shell=True, universal_newlines=True )).replace('\n','')

    json_files = glob.glob(dirname + "/*cl*.json")
    
    for file in json_files:
        print(file)
        f = open(file, 'r')
        perf_dict = json.load(f)

        init_plt()
    
        x = np.array(range(len(perf_dict["intervals"])))
        y = np.array([])
        
        for p in perf_dict["intervals"]:
            y = np.append(y, p["sum"]["bits_per_second"])
        
        plt.plot(x, y, "r",marker="o",markersize=2)
        
        plt.show()

# Start program
if __name__ == "__main__":
    main()
