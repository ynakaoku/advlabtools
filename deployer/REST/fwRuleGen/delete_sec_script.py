#!/usr/bin/env python

import argparse

# Constants - please change per NSX environment
NSX_RAML = '/home/vmware/nsxraml/vmware/nsxraml/nsxvapi.raml'
NSX_IP = '172.16.180.112'
NSX_USER = 'admin'
NSX_PASS = 'VMware1!'
VALID_RULE_SECTION = '1004'

# Shell snippets for building shell script executes curl commands
script_header_snippet = '#! /bin/bash\n'
script_delete_snippet = 'curl -s -o /tmp/delete.stdout -k -u ' + NSX_USER + ':' + NSX_PASS + ' -X DELETE "https://' + NSX_IP + '/api/4.0/firewall/globalroot-0/config/layer3sections/%s"\n'

def get_args():
    parser = argparse.ArgumentParser(
        description='Python script for generating shell script and XML data files. Shell script execute curl commands to kick DFW Delete method (DELETE) of NSX Managaer for removing NSX DFW sections. Number of dummy sections and rules can be configured with parameters.')

    parser.add_argument('-i', '--id',
                        required=True,
                        action='store',
                        help='Unique ID for generated file')

    parser.add_argument('-s', '--sections',
                        required=False,
                        default=1,
                        action='store',
                        help='number of sections')

    parser.add_argument('-r', '--rules',
                        required=False,
                        default=1,
                        action='store',
                        help='number of rules per single section')

    args = parser.parse_args()

#    if not args.vcenter_password:
#        args.vcenter_password = getpass.getpass(
#            prompt='Enter password for host %s and user %s: ' %
#                   (args.vcenter, args.vcenter_user))
#    if not args.nsx_password:
#        args.nsx_password = getpass.getpass(
#            prompt='Enter password for host %s and user %s: ' %
#                   (args.nsxmgr, args.nsx_user))
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

def get_section_id(client_session, section_name):
    section_list = []
    query_parameters_dict = {'name': section_name}

    dfw_section_details = dict(client_session.read('dfwL3Section', query_parameters_dict=query_parameters_dict))

#    section_name = dfw_section_details['body']['sections']['section']['@name']
    section_id = dfw_section_details['body']['sections']['section']['@id']
#    section_type = dfw_section_details['body']['sections']['section']['@type']
#    section_etag = dfw_section_details['Etag']
#    section_list.append((section_name, section_id, section_type, section_etag))

    return section_id

def main():
    args = get_args()
    
    s_max = int(args.sections)
    r_max = int(args.rules)

    from nsxramlclient.client import NsxClient
    client_session=NsxClient(NSX_RAML, NSX_IP, NSX_USER, NSX_PASS)

    script = script_header_snippet

    s_count = 0

    while s_count < s_max :   
        sid = get_section_id(client_session, "Section_"+str(s_count))
        script = script + script_delete_snippet % sid
        s_count = s_count + 1

    write_body_to_file(script, args.id + '.bash' )

if __name__ == '__main__':
    main()
