import subprocess
import json
import logging
import sys

from shutil import which
from pprint import pprint

from netbox_agent.misc import is_tool


class OVS():
    def __init__(self):
        print("ovs init")

        if which('ovs-vsctl') is None:
            print("could not find ovs-vsctl")
            return

        status, output = subprocess.getstatusoutput("ovs-vsctl show")

        if status != 0:
            print("ovs-vsctl failed.")
            return

        self.fields = {}
        field = ''

        for line in output.split('\n'):
            line = line.rstrip()
            r = line.split(" ")[-2:]
            # print("line: %s" % line)
            # print("split: %s" % r )

            if len(r) < 2:
                 self.fields["info"] = {}
                 self.fields["info"]["switch_uuid"] = r[0]

            if "Bridge" in r[0]:
                 bridge = r[1]
            if "Port" in r[0]:
                 port = r[1]
                 self.fields[port] = {}
                 self.fields[port]["port"] = r[1]
                 self.fields[port]["bridge"] = bridge
            if "tag" in r[0]:
                 self.fields[port]["vlan"] = r[1]
            if "Interface" in r[0]:
                 self.fields[port]["interface"] = r[1]
            if "type" in r[0]:
                 self.fields[port]["type"] = r[1]
            if "options" in r[0]:
                 self.fields[port]["options"] = r[1]
            if "ovs_version" in r[0]:
                 self.fields["info"]["ovs_version"] = r[1]
            
        print("ovs vsctl ran..")
        pprint(self.fields)


    def get_info(self, interface):
       for interface in self.fields:
           if "interface" in self.fields[interface]:
               if interface in self.fields[interface]["interface"]:
                   return(self.fields[interface])
