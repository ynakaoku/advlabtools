#!/usr/bin/env python

import argparse

# Constants - please change per NSX environment
NSX_IP = '172.16.130.242'
NSX_USER = 'admin'
NSX_PASS = 'vmwareNSX1!'
EDGE_ID = 'edge-6'

# XML snippets for building NSX DFW section schema
rules_header_snippet = '<firewallRules>\n'
rules_tailer_snippet = '</firewallRules>'
dummy_rule_snippet = '<firewallRule><name>Rule_%s</name><source><exclude>false</exclude><ipAddress>%s</ipAddress></source><destination><exclude>false</exclude><ipAddress>172.16.17.100</ipAddress></destination><action>accept</action></firewallRule>\n'

# Shell snippets for building shell script executes curl commands
script_header_snippet = '#! /bin/bash\n'
script_post_1_snippet = 'curl -s -o /tmp/%s.stdout -k -u ' + NSX_USER + ':' + NSX_PASS + ' -X POST -d @./%s -H "Content-Type: application/xml"  "https://' + NSX_IP + '/api/4.0/edges/%s/firewall/config/rules"\n'

def get_args():
    parser = argparse.ArgumentParser(
        description='Python script for generating shell script and XML data files. Shell script execute curl commands to kick Edge Firewall Rules Create method (POST) of NSX Managaer for inserting NSX Edge Rules to specified Edge node. Number of dummy rules can be configured with parameters. This script does not generate valid rules which must be created manually beforehand. Unique IP Addresses for dummy rules are also generated automatically.')

    parser.add_argument('-i', '--id',
                        required=True,
                        action='store',
                        help='Unique ID for generated file')

    parser.add_argument('-r', '--rules',
                        required=False,
                        default=1,
                        action='store',
                        help='number of rules')

    args = parser.parse_args()

    return args

def write_body_to_file(body, fname):
    """
    This function write xml body string to specific file
    :param body: string include xml body schema, script body, etc..
    :param fname: output file name
    """
    f = open('./' + fname, 'w')
    f.write(body)
    f.close()

def write_xml_body(xml, fid, sid):
    """
    This function write xml body string to specific file
    :param xml: string include xml body schema.
    :param fid: string for identify the project file
    :param sid: string for identify the section id
    """
    TEMP_FILE = './body_%s_s%s.xml' % (fid, str(sid) )

    f = open(TEMP_FILE, 'w')
    f.write(xml)
    f.close()

def get_ipv4address(r_count):
    oct3 = r_count / 256
    oct4 = r_count - (256 * oct3)
    return "172.16." + str(oct3) + "." + str(oct4)

def gen_dummy_rules(r_max):
    xml = ""
    r_count = 0
    while r_count < r_max :
        xml = xml + dummy_rule_snippet % (r_count, get_ipv4address(r_count))
        r_count = r_count + 1
    return xml

def main():
    args = get_args()
    
    r_max = int(args.rules)

    script = script_header_snippet
    script_post_snippet = script_post_1_snippet

    xml = rules_header_snippet
    xml = xml + gen_dummy_rules(r_max)
    xml = xml + rules_tailer_snippet
    xml_file = '%s.xml' % args.id
    write_body_to_file(xml, xml_file)
    script = script + script_post_snippet % ( xml_file, xml_file, EDGE_ID )

    write_body_to_file(script, args.id + '.bash' )

if __name__ == '__main__':
    main()
