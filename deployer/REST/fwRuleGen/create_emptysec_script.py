#!/usr/bin/env python

import argparse

# Constants - please change per NSX environment
NSX_IP = '172.16.180.112'
NSX_USER = 'admin'
NSX_PASS = 'VMware1!'
VALID_RULE_SECTION = '1004'

# XML snippets for building NSX DFW section schema
section_header_snippet = '<section name="Section_%s">'
section_tailer_snippet = '</section>'

# Shell snippets for building shell script executes curl commands
script_header_snippet = '#! /bin/bash\n'
script_post_1_snippet = 'curl -s -o /tmp/%s.stdout -k -u ' + NSX_USER + ':' + NSX_PASS + ' -X POST -d @./%s -H "Content-Type: application/xml"  "https://' + NSX_IP + '/api/4.0/firewall/globalroot-0/config/layer3sections?operation=insert_before_default"\n'
script_post_2_snippet = 'curl -s -o /tmp/%s.stdout -k -u ' + NSX_USER + ':' + NSX_PASS + ' -X POST -d @./%s -H "Content-Type: application/xml"  "https://' + NSX_IP + '/api/4.0/firewall/globalroot-0/config/layer3sections?operation=insert_before&anchorId=' + VALID_RULE_SECTION + '"\n'

def get_args():
    parser = argparse.ArgumentParser(
        description='Python script for generating shell script and XML data files. Shell script execute curl commands to kick DFW Create method (POST) of NSX Managaer for inserting empty NSX DFW sections for test purpose. Number of dummy sections and rules can be configured with parameters.')

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

    parser.add_argument('-p', '--position',
                        required=False,
                        default='tail',
                        action='store',
                        help='position of valid rule: head or tail(default)')

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

def gen_dummy_sections(s_count, r_max):
    xml = ""
    r_count = 0
    while r_count < r_max :   
        xml = xml + dummy_rule_snippet % (s_count, r_count)
        r_count = r_count + 1
    return xml

def main():
    args = get_args()
    
    s_max = int(args.sections)
    r_max = int(args.rules)

    script = script_header_snippet
    if args.position == 'head':
        script_post_snippet = script_post_2_snippet
    elif args.position == 'tail':
        script_post_snippet = script_post_1_snippet
    else:
        print "Position for dummy sections is not correct. Must be 'head' or 'tail'."
        exit(0)

    s_count = 0

    while s_count < s_max :   
        xml = section_header_snippet % s_count
        xml = xml + section_tailer_snippet
        xml_file = '%s_s%s.xml' % (args.id, str(s_count) )
        write_body_to_file(xml, xml_file)
        script = script + script_post_snippet % ( xml_file, xml_file )
        s_count = s_count + 1

    write_body_to_file(script, args.id + '.bash' )

if __name__ == '__main__':
    main()
