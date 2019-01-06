#!/usr/bin/env python

import argparse

# Constants - please change per NSX environment
NSX_IP = '172.16.170.130'
NSX_USER = 'admin'
NSX_PASS = 'VMware1!'

# XML snippets for building NSX DFW section schema
section_header_snippet = '<section name="Section_%s">'
section_tailer_snippet = '</section>'
dummy_rule_snippet = '<rule logged="false" disabled="false"><direction>inout</direction><name>Rule_%s_%s</name><notes></notes><sources excluded="false"><source><type>Ipv4Address</type><value>10.10.10.0/24</value></source></sources><tag></tag><services><service><protocolName>TCP</protocolName><destinationPort>5001</destinationPort></service></services><appliedToList><appliedTo><value>DISTRIBUTED_FIREWALL</value></appliedTo></appliedToList><packetType>any</packetType><action>deny</action><destinations excluded="false"><destination><type>Ipv4Address</type><value>172.16.173.211</value></destination></destinations></rule>'
valid_rule_snippet = '<rule logged="false" disabled="false"><direction>inout</direction><name>Valid_Rule</name><notes></notes><sources excluded="false"><source><type>Ipv4Address</type><value>172.16.173.212</value></source></sources><tag></tag><appliedToList><appliedTo><value>DISTRIBUTED_FIREWALL</value></appliedTo></appliedToList><packetType>any</packetType><action>allow</action><destinations excluded="false"><destination><type>Ipv4Address</type><value>172.16.173.211</value></destination></destinations></rule>'

# Shell snippets for building shell script executes curl commands
script_header_snippet = '#! /bin/bash\n'
script_post_snippet = 'curl -s -o /tmp/%s.stdout -k -u ' + NSX_USER + ':' + NSX_PASS + ' -X POST -d @./%s -H "Content-Type: application/xml"  https://' + NSX_IP + '/api/4.0/firewall/globalroot-0/config/layer3sections?operation=insert_before_default\n'

# Ansible Playbook snippets for building section inventory for deleting
pbook_sections_header_snippet = "dfw_sections:\n"
pbook_sections_body_snippet = "    - name: 'Section_%s'\n"

def get_args():
    parser = argparse.ArgumentParser(
        description='Python script for generating Ansible Playbook file which describes NSX DFW sections and rules. Number of dummy sections and rules can be configured with parameters.')

    parser.add_argument('-i', '--id',
                        required=True,
                        action='store',
                        help='Unique ID for generated playbook file')

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

    parser.add_argument('-v', '--valid',
                        required=False,
                        default='yes',
                        action='store',
                        help='set \'no\' if not include a valid rule: yes or no')

    parser.add_argument('-p', '--position',
                        required=False,
                        default='tail',
                        action='store',
                        help='position of valid rule: head or tail')

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

def write_xml_body(xml, fid, sid):
    """
    This function write xml body string to specific file
    :param xml: string include xml body schema.
    :param fid: string for identify the project file
    :param sid: string for identify the section id
    """
#    now = time()

    TEMP_FILE = './body_%s_s%s.xml' % (fid, str(sid) )

#    print xml

    f = open(TEMP_FILE, 'w')
    f.write(xml)
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

    if args.position != 'head' and args.position != 'tail':
        print "Position param for valid rule is not correct. Must be 'head' or 'tail'."
        exit(0)

    script = script_header_snippet
    pbook = pbook_sections_header_snippet

    if args.valid == 'yes':
        s_count = 0
        xml = section_header_snippet % s_count

        if args.position == 'head':
            xml = xml + valid_rule_snippet
            xml = xml + gen_dummy_sections(s_count, r_max-1)
            xml = xml + section_tailer_snippet
            xml_file = '%s_s%s.xml' % (args.id, str(s_count) )
            write_body_to_file(xml, xml_file)
            script = script + script_post_snippet % ( xml_file, xml_file )
            pbook = pbook + pbook_sections_body_snippet % str(s_count)
        elif args.position == 'tail':
            s_max = s_max - 1
            if s_max > 0:
                xml = xml + gen_dummy_sections(s_count, r_max)
                xml = xml + section_tailer_snippet
                xml_file = '%s_s%s.xml' % (args.id, str(s_count) )
                write_body_to_file(xml, xml_file)
                script = script + script_post_snippet % ( xml_file, xml_file )
                pbook = pbook + pbook_sections_body_snippet % str(s_count)

        s_count = s_count + 1
        while s_count < s_max :   
            xml = section_header_snippet % s_count
            xml = xml + gen_dummy_sections(s_count, r_max)
            xml = xml + section_tailer_snippet
            xml_file = '%s_s%s.xml' % (args.id, str(s_count) )
            write_body_to_file(xml, xml_file)
            script = script + script_post_snippet % ( xml_file, xml_file )
            pbook = pbook + pbook_sections_body_snippet % str(s_count)
            s_count = s_count + 1

        if args.position == 'tail':
            xml = section_header_snippet % s_count
            xml = xml + gen_dummy_sections(s_count, r_max-1)
            xml = xml + valid_rule_snippet
            xml = xml + section_tailer_snippet
            xml_file = '%s_s%s.xml' % (args.id, str(s_count) )
            write_body_to_file(xml, xml_file)
            script = script + script_post_snippet % ( xml_file, xml_file )
            pbook = pbook + pbook_sections_body_snippet % str(s_count)

    elif args.valid == 'no':
        s_count = 0
        while s_count < s_max :   
            xml = section_header_snippet % s_count
            xml = xml + gen_dummy_sections(s_count, r_max)
            xml = xml + section_tailer_snippet
            xml_file = '%s_s%s.xml' % (args.id, str(s_count) )
            write_body_to_file(xml, xml_file)
            script = script + script_post_snippet % ( xml_file, xml_file )
            pbook = pbook + pbook_sections_body_snippet % str(s_count)
            s_count = s_count + 1

    else:
        print "Flag for Valid rule is not correct. Must be 'yes' or 'no'."
        exit(0)

    write_body_to_file(script, args.id + '.bash' )
    write_body_to_file(pbook, 'dfw_sections.yml' )

if __name__ == '__main__':
    main()
