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

ofdpa_instance = ofdpa.OFDPA(mode="ODL", controller_ip="10.10.10.254", ofdpa_id="openflow:55932")

# Configure topology. In this case, two servers with two NICs each, and one
# OFDPA switch
switch, nyx, ananke = topo.create_basic_tue_lab()

# Start up the ping use case. After sending sending this to the ODL controller
# with .ODL/send.py, the clients should be able to ping.
node_3_mac = 0x90e2ba1fe649
# Node 1 connected to port xe45 of TOR 1
node_1_tor_1_port = 46
# port xe46 of TOR 1 connected to port xe46 of TOR2
tor_1_tor_2_port = 47
# port xe47 of TOR 2 connected to port xe47 of TOR3
tor_2_tor_3_port = 48
# port xe45 of TOR 3 connected to node 3
tor_3_node_3_port = 46
node_1_mac = 0x90e2ba1fdfd1
dummy_vlan = 10

# port xe48 of TOR 1 connected to polatis
# port xe48 of TOR 2 connected to polatis
# port xe48 of TOR 3 connected to polatis
tor_1_polatis = 49
tor_2_polatis = 49
tor_3_polatis = 49

# Allow traffic coming from port tor_3_polatis
ofdpa.VLAN_VLAN_Filtering_Flow(ofdpa_instance, tor_3_polatis, dummy_vlan)
ofdpa.VLAN_Untagged_Packet_Port_VLAN_Assignment_Flow(ofdpa_instance,
                                                         tor_3_polatis,
                                                         dummy_vlan)

# Route traffic with dscp=60 and eth_dst=node_3_mac to tor_3_node_3_port
dscp = 63
l2_Interface_group = ofdpa.L2_Interface_Group(ofdpa_instance,
                                              tor_3_node_3_port,
                                              dummy_vlan,
                                              pop_vlan=True)
ofdpa.Policy_ACL_IPv4_VLAN_Flow(ofdpa_instance,
                               l2_Interface_group,
                               IP_DSCP=dscp,
                               ETH_DST=node_3_mac)

# Route traffic with dscp=60 and eth_dst=node_1_mac to tor_3_polatis
l2_Interface_group = ofdpa.L2_Interface_Group(ofdpa_instance,
                                              tor_3_polatis,
                                              dummy_vlan,
                                              pop_vlan=True)
ofdpa.Policy_ACL_IPv4_VLAN_Flow(ofdpa_instance,
                               l2_Interface_group,
                               IP_DSCP=dscp,
                               ETH_DST=node_1_mac)

ofdpa_instance.ODL_instance.write_to_file()
print "WARNING!! Don't forget to change the flow_ids to avoid collisions! Send.py is dumb!"

# Remove the fake datapath that got created earlier to be sure. If you keep
# opening a new python console to run, you shouldn't need this.
ofdpa._remove_fake_datapath()
