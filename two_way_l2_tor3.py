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

# When all switches are configured, all compute nodes should be able to ping.
with open('topology', 'r') as file_:
    for line in file_:
        if not line.startswith('#') and line != '\n':
            stripped = [x.strip() for x in line.split('=')]
            globals()[stripped[0]] = int(stripped[1], 0)

dummy_vlan = 10
# Allow traffic from the XENA tester port 0
ofdpa.VLAN_VLAN_Filtering_Flow(ofdpa_instance, tor_3_xena_0_port, dummy_vlan)
ofdpa.VLAN_Untagged_Packet_Port_VLAN_Assignment_Flow(ofdpa_instance,
                                                     tor_3_xena_0_port,
                                                     dummy_vlan)
# Allow traffic from the XENA tester port 5
ofdpa.VLAN_VLAN_Filtering_Flow(ofdpa_instance, tor_3_xena_5_port, dummy_vlan)
ofdpa.VLAN_Untagged_Packet_Port_VLAN_Assignment_Flow(ofdpa_instance,
                                                     tor_3_xena_5_port,
                                                     dummy_vlan)
# Allow traffic from TOR2
ofdpa.VLAN_VLAN_Filtering_Flow(ofdpa_instance, tor_2_tor_3_port, dummy_vlan)
ofdpa.VLAN_Untagged_Packet_Port_VLAN_Assignment_Flow(ofdpa_instance,
                                                     tor_2_tor_3_port,
                                                     dummy_vlan)
# Allow traffic compute node 3
ofdpa.VLAN_VLAN_Filtering_Flow(ofdpa_instance, tor_3_node_3_port, dummy_vlan)
ofdpa.VLAN_Untagged_Packet_Port_VLAN_Assignment_Flow(ofdpa_instance,
                                                     tor_3_node_3_port,
                                                     dummy_vlan)
# Allow traffic from Polatis port
ofdpa.VLAN_VLAN_Filtering_Flow(ofdpa_instance, tor_2_tor_3_polatis, dummy_vlan)
ofdpa.VLAN_Untagged_Packet_Port_VLAN_Assignment_Flow(ofdpa_instance,
                                                     tor_2_tor_3_polatis,
                                                     dummy_vlan)


# Reroute traffic matching compute node 3 MAC to the compute node 3 port
l2_interface_group = ofdpa.L2_Interface_Group(ofdpa_instance,
                                              tor_3_node_3_port,
                                              dummy_vlan,
                                              pop_vlan=True)
ofdpa.Bridging_Unicast_VLAN_Bridging_Flow(ofdpa_instance,
                                          dummy_vlan,
                                          node_3_mac,
                                          l2_interface_group)

# Reroute traffic matching compute node 1 MAC to TOR2 port
l2_interface_group = ofdpa.L2_Interface_Group(ofdpa_instance,
                                              tor_2_tor_3_port,
                                              dummy_vlan,
                                              pop_vlan=True)
ofdpa.Bridging_Unicast_VLAN_Bridging_Flow(ofdpa_instance,
                                          dummy_vlan,
                                          node_1_mac,
                                          l2_interface_group)

# Reroute traffic matching compute node 2 MAC to TOR2 port
ofdpa.Bridging_Unicast_VLAN_Bridging_Flow(ofdpa_instance,
                                          dummy_vlan,
                                          node_2_mac,
                                          l2_interface_group)

# Reroute traffic matching XENA port 1 MAC to TOR2 port
ofdpa.Bridging_Unicast_VLAN_Bridging_Flow(ofdpa_instance,
                                          dummy_vlan,
                                          xena_1_mac,
                                          l2_interface_group)

# Reroute traffic matching XENA port 2 MAC to TOR2 port
ofdpa.Bridging_Unicast_VLAN_Bridging_Flow(ofdpa_instance,
                                          dummy_vlan,
                                          xena_2_mac,
                                          l2_interface_group)

# Reroute traffic matching XENA port 4 MAC to TOR2 port
ofdpa.Bridging_Unicast_VLAN_Bridging_Flow(ofdpa_instance,
                                          dummy_vlan,
                                          xena_4_mac,
                                          l2_interface_group)

# Reroute traffic matching XENA port 0 to XENA port
l2_interface_group = ofdpa.L2_Interface_Group(ofdpa_instance,
                                              tor_3_xena_0_port,
                                              dummy_vlan,
                                              pop_vlan=True)
ofdpa.Bridging_Unicast_VLAN_Bridging_Flow(ofdpa_instance,
                                          dummy_vlan,
                                          xena_0_mac,
                                          l2_interface_group)

# Reroute traffic matching XENA port 5 MAC to XENA port
l2_interface_group = ofdpa.L2_Interface_Group(ofdpa_instance,
                                              tor_3_xena_5_port,
                                              dummy_vlan,
                                              pop_vlan=True)
ofdpa.Bridging_Unicast_VLAN_Bridging_Flow(ofdpa_instance,
                                          dummy_vlan,
                                          xena_5_mac,
                                          l2_interface_group)


ofdpa_instance.ODL_instance.write_to_file()

# Remove the fake datapath that got created earlier to be sure. If you keep
# opening a new python console to run, you shouldn't need this.
ofdpa._remove_fake_datapath()
