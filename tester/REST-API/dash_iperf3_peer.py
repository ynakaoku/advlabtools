#! /usr/bin/env python3
# -*- coding: utf-8 -*-
# Filename: k8s_iperf_peer.py, part of advlabtools; https://github.com/ynakaoku/advlabtools
# Author: Yoshihiko Nakaoku; ynakaoku@vmware.com

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
#import pandas as pd
import os
#import commands
import subprocess
import json
#import argparse
import glob
import csv, re
import yaml
from kubernetes import config
# from kubernetes.client import Configuration
from kubernetes.client.apis import core_v1_api
# from kubernetes.client.rest import ApiException
# from kubernetes.stream import stream
from flask import Flask, jsonify, request, Markup, abort, make_response
from dash import Dash
import dash_html_components as html

### REST API definitions
api = Flask(__name__)

@api.route('/')
def index():
    html = '''
    Start Page
    '''
    return Markup(html)

@api.route('/iperf3')
def iperf3_input():
    html = '''
    <form action="/iperf3/RunTest">
        <p><label>iperf3 test: </label></p>
        Test Name: <input type="text" name="TestName"></p>
        Config File: <input type="text" name="ConfigFile"></p>
        Interval: <input type="text" name="Interval" value="1"></p>
        Bandwidth: <input type="text" name="Bandwidth" value="1G"></p>
        MSS: <input type="text" name="MSS" value="1460"></p>
        Parallel: <input type="text" name="Parallel" value="1"></p>
        Time: <input type="text" name="Time" value="10"></p>
        Protocol is UDP? : <input type="checkbox" name="UDP?"></p>
        Use Server Output? : <input type="checkbox" name="Get Server Output?"></p>
        Use ESXTOP Output? : <input type="checkbox" name="Get ESXTOP Output?"></p>
        <button type="submit" formmethod="post">POST</button></p>
    </form>
    '''
    return Markup(html)

@api.route('/iperf3/RunTest', methods=['POST'])
def iperf3RunTest():
    content = request.get_json()
#    print (content)
    try:
#        return Markup(content)
        return iperf3_run_test(content)
    except Exception as e:
        return str(e)

@api.route('/iperf3/GetTestDetails', methods=['GET'])
def iperf3TestDetails():
    testid = request.args.get('testid')
    try:
        return iperf3_get_test_details(testid)
    except Exception as e:
        return str(e)

@api.route('/iperf3/GetTestHistory', methods=['GET'])
def iperf3TestHistory():
    try:
        return iperf3_get_test_history()
    except Exception as e:
        return str(e)

@api.route('/sayHello', methods=['GET'])
def say_hello():

    result = {
        "result":True,
        "data": "Hello, world!"
        }

    return make_response(jsonify(result))
    # if you do not want to use Unicode: 
    # return make_response(json.dumps(result, ensure_ascii=False))

@api.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# RDICT definitions for ESXTOP processing
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

# Matplotlib Formatter definitions
class FixedOrderFormatter(ticker.ScalarFormatter):
    def __init__(self, order_of_mag=0, useOffset=True, useMathText=True):
        self._order_of_mag = order_of_mag
        ticker.ScalarFormatter.__init__(self, useOffset=useOffset, 
                                 useMathText=useMathText)
    def _set_orderOfMagnitude(self, range):
        self.orderOfMagnitude = self._order_of_mag

# get options for shel script
def get_option(content):
    print("[Test parameters per Peers]")
    options = " -C /tmp/advlabtools-scenario-temp -N " + content['testName'] + " -J -s "
    if content['proto'] is 'udp':
        options = options + " -u "
        print("| Protocol: UDP", end=" ")
    else:
        print("| Protocol: TCP", end=" ")
    if content['bandwidth']:
        options = options + " -b " + content['bandwidth']
        print("| Bandwidth(bps): " + content['bandwidth'], end=" ")
    else:
        if content['proto'] is 'udp':
          print("| Bandwidth(bps): 1M", end=" ")
        else:
          print("| Unlimitted Bandwidth", end=" ")
    if content['mss']:
        options = options + " -M " + str(content['mss'])
        print("| MSS(byte): " + str(content['mss']), end=" ")
    else:
        print("| MSS(byte): 1460", end=" ")
    if content['parallel']:
        options = options + " -P " + str(content['parallel'])
        print("| Streams: " + str(content['parallel']), end=" ")
    else:
        print("| Streams: 1", end=" ")
    if content['interval']:
        options = options + " -i " + str(content['interval'])
        print("| Interval(s): " + str(content['interval']), end=" ")
    else:
        print("| Interval(s): 1", end=" ")
    if content['time']:
        options = options + " -t " + str(content['time'])
        print("| Time(s): " + str(content['time']), end=" ")
    else:
        print("| Time(s): 10", end=" ")
    if content['useEsxtopOutput']:
        options = options + " -E "
        print("| Capture ESXTOP", end=" ")
    if content['useServerOutput']:
        options = options + " -G "
        print("| Use Server side data", end=" ")
    else:
        print("| Use Client side data")

    return options

# Matplotlib plot initialization
def init_plt():
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

# get iperf3 test history
def iperf3_get_test_history():
    list_dict = { os.listdir(path='reports') }
    list_json = json.dumps(list_dict)
    print(list_json)
    return make_response(list_json)
    
# get details of an iperf3 test specified with testid
def iperf3_get_test_details(testid):
    f = open('reports/' + testid + '/TestDetails.json', 'r')
    detail = json.load(f)
#    print(detail)
    return make_response(jsonify(detail))
    
# run iperf3 test workflow
def iperf3_run_test(content):
    
    config.load_kube_config() 
#    c = Configuration() 
#    c.assert_hostname = False
#    Configuration.set_default(c) 
    api = core_v1_api.CoreV1Api() 
#    name = 'busybox-test'

    # connect k8s and read test containers
    #v1 = client.CoreV1Api()
    #ret = v1.list_pod_for_all_namespaces(label_selector="app=iperf3", watch=False)
    pods = api.list_pod_for_all_namespaces(label_selector="app=iperf3", watch=False)
    
    # check if each pods are READY

    # update scenario data with real container name
    servers=[]
    targets=[]
    clients=[]
    stypes=[]
    ctypes=[]
    snamespaces=[]
    cnamespaces=[]
    mode=content['mode']
    proto=content['proto']

    for i in content['flows']:
        stypes.append(i['server']['type'])
        ctypes.append(i['client']['type'])
        targets.append(i['target'])
        if i['server']['type'] == 'kubernetes':
            for j in pods.items:
                if j.spec.hostname == i['server']['name']:
                    servers.append(j.metadata.name)
                    snamespaces.append(j.metadata.namespace)
        else:
            servers.append(i['server']['name'])
            snamespaces.append("")

        if i['client']['type'] == 'kubernetes':
            for j in pods.items:
                if j.spec.hostname == i['client']['name']:
                    clients.append(j.metadata.name)
                    cnamespaces.append(j.metadata.namespace)
        else:
            clients.append(i['server']['name'])
            cnamespaces.append("")
#        print("%s\t%s\t%s" % (i.status.pod_ip, i.metadata.namespace, i.metadata.name))
    f = open("/tmp/advlabtools-scenario-temp", "w")
    test_str = ""
    servers_str = ""
    for s in servers: servers_str += '"' + s + '" '
    test_str += 'servers=(' + servers_str + ')\n'
    targets_str = ""
    for s in targets: targets_str += '"' + s + '" '
    test_str += 'targets=(' + targets_str + ')\n'
    clients_str = ""
    for s in clients: clients_str += '"' + s + '" '
    test_str += "clients=(" + clients_str + ")\n"
    stypes_str = ""
    for s in stypes: stypes_str += '"' + s + '" '
    test_str += "stypes=(" + stypes_str + ")\n"
    ctypes_str = ""
    for s in ctypes: ctypes_str += '"' + s + '" '
    test_str += "ctypes=(" + ctypes_str + ")\n"
    snamespaces_str = ""
    for s in snamespaces: snamespaces_str += '"' + s + '" '
    test_str += "snamespaces=(" + snamespaces_str + ")\n"
    cnamespaces_str = ""
    for s in cnamespaces: cnamespaces_str += '"' + s + '" '
    test_str += "cnamespaces=(" + cnamespaces_str + ")\n"
    test_str += 'mode="' + mode + '"\n' + 'proto="' + proto + '"'
#    print(test_str)
    f.write(test_str)
    f.close()

#    exec_command1 = ['iperf3', '-s']
#    resp1 = stream(api.connect_get_namespaced_pod_exec, 'iperf3-dep1-7bb5958b8d-vjg6n', 'default', command=exec_command1, stderr=True, stdin=False, stdout=True, tty=False)
#    exec_command2 = ['iperf3', '-J', '-c', 'iperf3-dep1', '-t', '10']
#    resp2 = stream(api.connect_post_namespaced_pod_exec, 'iperf3-dep2-64b64896fb-msrxt', 'default', command=exec_command2, stderr=True, stdin=False, stdout=True, tty=False)
#
#    while True:
#        if not resp2.is_open():
#            resp2.peek_stdout()
#            resp1.close()
#            break

    cmd = "../scripts/k8s_iperf3_peer.bash "
    cmd_options = get_option(content)

    print('Testing, wait {} seconds... '.format(content['time']), end=" ")
    dirname = str(subprocess.check_output( cmd+cmd_options, shell=True, universal_newlines=True )).replace('\n','')
    testid = dirname.split("/")[-1]
    print('done')

    content['result'] = {}
    content['result']['directory'] = dirname
    content['result']['id'] = testid

    json_files = glob.glob(dirname + "/*cl*.json")
    print("[Test Result]")
    print("| Number of peers: " + str(len(json_files)))
    content['result']['peers'] = len(json_files) 

    csv_files = glob.glob(dirname + "/*esxtop*.csv")
    print("[Test Result]")
    print("| Number of hosts: " + str(len(csv_files)))
    print("")
    content['result']['hosts'] = len(csv_files) 

    x={}
    y={}
    t=np.zeros(int(content['time']))
    i=0

    init_plt()
    
    for file in json_files:
        print(file)
        flowid = file.split("/")[-1]
        content['result'][flowid] = {}

        f = open(file, 'r')
        perf_dict = json.load(f)

        if proto is 'udp':
            print("| Avg Bandwidth(Gbps): " + str(perf_dict["end"]["sum"]["bits_per_second"] / 1000000000), end=" ")
            content['result'][flowid]['bits_per_second'] = perf_dict["end"]["sum"]["bits_per_second"]

            print("| Jitter(ms): " + str(perf_dict["end"]["sum"]["jitter_ms"]), end=" ")
            content['result'][flowid]['jitter'] = perf_dict["end"]["sum"]["jitter_ms"]

            print("| Lost Packets: " + str(perf_dict["end"]["sum"]["lost_packets"]), end=" ")
            content['result'][flowid]['lost_packets'] = perf_dict["end"]["sum"]["lost_packets"]

            print("| Lost %: " + str(perf_dict["end"]["sum"]["lost_percent"]))
            content['result'][flowid]['lost_percent'] = perf_dict["end"]["sum"]["lost_percent"]

            print("| Sender CPU%: " + str(perf_dict["end"]["cpu_utilization_percent"]["host_total"]), end=" ")
            content['result'][flowid]['local_cpu_utilization'] = perf_dict["end"]["cpu_utilization_percent"]["host_total"]

            print("| Receiver CPU%: " + str(perf_dict["end"]["cpu_utilization_percent"]["remote_total"]))
            content['result'][flowid]['remote_cpu_utilization'] = perf_dict["end"]["cpu_utilization_percent"]["remote_total"]

        else:
            print("| Avg Bandwidth(Gbps): " + str(perf_dict["end"]["sum_received"]["bits_per_second"] / 1000000000), end=" ")
            content['result'][flowid]['bits_per_second'] = perf_dict["end"]["sum_received"]["bits_per_second"]

            print("| Retransmits: " + str(perf_dict["end"]["sum_sent"]["retransmits"]))
            content['result'][flowid]['retransmits'] = perf_dict["end"]["sum_sent"]["retransmits"]

            print("| Sender CPU%: " + str(perf_dict["end"]["cpu_utilization_percent"]["host_total"]), end=" ")
            content['result'][flowid]['local_cpu_utilization'] = perf_dict["end"]["cpu_utilization_percent"]["host_total"]

            print("| Receiver CPU%: " + str(perf_dict["end"]["cpu_utilization_percent"]["remote_total"]))
            content['result'][flowid]['remote_cpu_utilization'] = perf_dict["end"]["cpu_utilization_percent"]["remote_total"]

        x[i] = np.array(range(len(perf_dict["intervals"])))
        y[i] = np.array([])
        
        for p in perf_dict["intervals"]:
            y[i] = np.append(y[i], p["sum"]["bits_per_second"])
        
        plt.plot(x[i], y[i], color[i],marker="o",markersize=3)
        t=t+y[i]

        i=i+1
        
    plt.plot(x[0], t, "k", marker="X", markersize=5, linewidth=2)
#    plt.show()
    plt.savefig(dirname + '/throughput.png')

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
#        plt.show()
        plt.savefig(dirname + '/serverload.png')

    f = open(dirname + '/TestDetails.json', 'w')
    json.dump(content, f)
    f.close()

    res = { "result":True, "id":content['result']['id'] }
    return make_response(jsonify(res))

# Start program
if __name__ == "__main__":
    api.run(host='0.0.0.0', port=8000)
