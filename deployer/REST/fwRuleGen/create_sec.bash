#! /bin/bash
curl -s -o /tmp/create_sec_s0.xml.stdout -k -u admin:VMware1! -X POST -d @./create_sec_s0.xml -H "Content-Type: application/xml"  "https://172.16.170.130/api/4.0/firewall/globalroot-0/config/layer3sections?operation=insert_before_default"
