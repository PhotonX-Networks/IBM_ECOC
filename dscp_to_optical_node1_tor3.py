#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module contains an example how to use the ofdpy use cases in combination
with an ODL controller.

@author: Karel van de Plassche
@licence: GPLv3
"""
import logging

from ofdpy import ofdpa
from ofdpy import usecase
from ofdpy import topology as topo

# Configure logging levels
# We only need to see warnings
logging.basicConfig(level=logging.WARN)
logger = logging.getLogger(__name__)
logging.getLogger("dicttoxml").setLevel(logging.WARN)

# But like some debug information from the messy ofdpy.odlparse
ch = logging.StreamHandler()
ch.setLevel(logging.WARN)
formatter = logging.Formatter('%(message)s')
ch.setFormatter(formatter)
logging.getLogger("ofdpy.odlparse").setLevel(logging.WARN)
logging.getLogger("ofdpy.odlparse").propagate = False
logging.getLogger("ofdpy.odlparse").addHandler(ch)

ofdpa_instance = ofdpa.OFDPA(mode="ODL", controller_ip="10.10.10.254", ofdpa_id="openflow:55932", flow_start=400)

with open('topology', 'r') as file_:
    for line in file_:
        if not line.startswith('#') and line != '\n':
            stripped = [x.strip() for x in line.split('=')]
            globals()[stripped[0]] = int(stripped[1], 0)

dummy_vlan = 10
dscp = 63
# We assume traffic from compute node 1 is allowed and Xena tester is allowed
l2_Interface_group = ofdpa.L2_Interface_Group(ofdpa_instance,
                                              tor_3_node_3_port,
                                              dummy_vlan,
                                              pop_vlan=True)
ofdpa.Policy_ACL_IPv4_VLAN_Flow(ofdpa_instance,
                           	l2_Interface_group,
                           	IP_DSCP=dscp,
                                ETH_DST=node_3_mac)

print ('WARNING! scripts are stupid. Change flow numbers to avoid collisions')
ofdpa_instance.ODL_instance.write_to_file()

# Remove the fake datapath that got created earlier to be sure. If you keep
# opening a new python console to run, you shouldn't need this.
ofdpa._remove_fake_datapath()
