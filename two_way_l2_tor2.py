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

ofdpa_instance = ofdpa.OFDPA(mode="ODL", controller_ip="10.10.10.254", ofdpa_id="openflow:55931")

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

ethernet_1_mac = 0x04F4BC1395C0
ethernet_2_mac = 0x04F4BC1395C1
# port xe51 of TOR 1 is connected to ethernet tester
tor_1_ethernet_1_port = 52
# port xe51 of TOR 3 is connected to ethernet tester
tor_3_ethernet_2_port = 52

dummy_vlan = 10
usecase.one_way_bridge(ofdpa_instance, dummy_vlan, tor_1_tor_2_port, (ethernet_2_mac, tor_2_tor_3_port))
usecase.one_way_bridge(ofdpa_instance, dummy_vlan, tor_2_tor_3_port, (ethernet_1_mac, tor_1_tor_2_port))

usecase.one_way_bridge(ofdpa_instance, dummy_vlan, tor_1_tor_2_port, (node_3_mac, tor_2_tor_3_port))
usecase.one_way_bridge(ofdpa_instance, dummy_vlan, tor_2_tor_3_port, (node_1_mac, tor_1_tor_2_port))
ofdpa_instance.ODL_instance.write_to_file()

# Remove the fake datapath that got created earlier to be sure. If you keep
# opening a new python console to run, you shouldn't need this.
ofdpa._remove_fake_datapath()
