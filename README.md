
#Summary
 - [Generation of the scripts](#generation-of-the-scripts)
 - [Preparation](#preparation)
 - [Default connection](#default-connection)
 - [Polatis rerouting](#polatis-rerouting)
   - [Use-case 1: Private circuit](#use-case-1-private-circuit)
   - [Use-case 2: Public circuit](#use-case-2-public-circuit)
   - [Use-case 3: All optical circuit](#use-case-3-all-optical-circuit)
   - [Use-case 4: Alternative route](#use-case-4-alternative-route)
 - [Debugging tools](#debuggin-tools)

# Generation of the scripts
All scripts in the repository are meant to be run on a device with OfdPy installed. Please have a look at https://github.com/PhotonX-Networks/OfdPy. These scripts then generate the necessary XML files that can then be send the the OpenDayLight OpenFlowPlugin REST API.

# Preparation
There are still some kinks to work our between ODL and the TUe TOR, so try to start as clean as possible. So:
- Start the ODL controller, from the controller node:

    ```
    ssh -p 65000 mininet@130.225.75.124
    cd ~/cosign/distribution/distributions/karaf/target/assembly/bin
    ./karaf clean -of13
    feature:install odl-base-all odl-aaa-authn odl-restconf odl-adsal-northbound odl-mdsal-apidocs odl-provisioningmanager
    feature:install odl-l2switch-switch # Gives a lot of errors on the switch, you can ignore them
    (feature:install odl-ovsdb-northbound)
    ```

- Close all agents on the TOR[1-3]:

    ```
    ssh root@10.10.10.[2-4]
    cd /root/ofdpa-photonx-tue-1.1.0.0
    killall ofagentapp*
    ```

- Start the agents on the TORs, preferably in a 'screen' environment. We're using ofagentapp.patched2 right now:

    ```
    screen
    ./ofagentapp.patched2 --controller=10.10.10.254:6633 --dpid=0x000000000000DA7[A-C] &
    ```

- The ODL controller and switches should now be empty. The topology managers should see the TORs. Try:
    - On the TORs, you check check group- and flowtables with:
    
        ```
        ./client_grouptable_dump
        ./client_flowtable_dump
        ```

    - Use the REST API of ODL to check the group- and flowtables. From anywhere inside the network:
    
        ```
        curl -u admin:admin http://10.10.10.254:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:5593[0-2]
        ```

    - Check for any leftover (optical) paths:

        ```
        curl -u admin:admin http://10.10.10.254:8181/restconf/config/optical-provisioning-manager:connections
        ```
    
# Default connection
Set up the 'default connection'; a L2-like bi-directional path between compute node 1, 2 and 3 and the Xena tester ports trough the three TORs. I've generated the necessary XML files to add all the flows and groups to ODL using the REST API. I also added a script how to send and delete them to ODL using Python transmissions. The use case is:    <br/>
CN1 <-> TOR1 <-> TOR2 <-> TOR3 <-> CN3 (normal + DSCP)    <br/>
CN2 <-> TOR2 <-> TOR3 <-> CN3 (normal + DSCP)             <br/>
XENA1 <-> TOR1 <-> TOR2 <-> TOR3 <-> XENA0                <br/>
XENA2 <-> TOR2 <-> TOR3 <-> XENA0                         <br/>
XENA4 <-> TOR2 <-> TOR3 <-> XENA5                         <br/>

- Add the flows to ODL. On the controller node:

    ``` 
    cd /home/ibm/tue_tor/OfdPy/examples/IBM_ECOC
    python send_usecase.py send 0
    ```

- The path should now be created. Check with a L2 ping (arping).
    - On compute node 1:

        ```
        sudo arping 30.30.30.2 -t 90:e2:ba:1f:e6:49
        ```

    - On compute node 3:

        ```
        sudo arping 30.30.30.1 -t 90:e2:ba:1f:df:d1
        ```

# Polatis rerouting
## Use-case 1: Private circuit
This use-case is meant to be used in combination with [Default connection](#Default connection). These scripts add the following flow:    <br/>
CN2 -> TOR2 -> Polatis -> TOR3 -> CN3 (DSCP)

- Add the flows to ODL. On the controller node:

    ``` 
    cd /home/ibm/tue_tor/OfdPy/examples/IBM_ECOC
    python send_usecase.py send 1
    ```

- Check rerouting with packeth (Assumes the optical path was created correctly):

    - On compute node 2:

        ```
        packeth
        ```

    - Load ibm > to_node3.packeth
    - Fill in:
        - Protocol = 00
        - TOS = 0xFC (DSCP 63)
    - Select interface `ens1f1`
    - Send packet
- When you're done, remove the rerouting:

    ```
    python send_usecase.py remove 1
    ```

## Use-case 2: Public circuit
This use-case is meant to be used in combination with [Default connection](#default-connection) and [Private circuit](#use-case-1-private-circuit). These scripts add the following flow:    <br/>
CN1 -> TOR1 -> TOR2 -> Polatis -> TOR3 -> CN3 (DSCP)

- Add the flows to ODL.  On the controller node:

    ``` 
    cd tue_tor/OfdPy/examples/IBM_ECOC
    python send_usecase.py send 2
    ```

- Check rerouting with packeth (Assumes the optical path was created correctly):

    - On compute node 2:

        ```
        packeth
        ```

    - Load ibm > to_node3.packeth
    - Fill in:
        - Protocol = 00
        - TOS = 0xFC (DSCP 63)
    - Select interface `ens1f1`
    - Send packet
- When you're done, remove the rerouting:

    ```
    python send_usecase.py remove 2
    ```

## Use-case 3: All optical circuit
- Remove the default case and add the flows to ODL. On the controller node:

    ``` 
    cd tue_tor/OfdPy/examples/IBM_ECOC
    python send_usecase.py remove 0
    python send_usecase.py send 3
    ```

- Check rerouting with packeth (Assumes the optical path was created correctly):

    - On compute node 2:

        ```
        packeth
        ```

    - Load ibm > to_node3.packeth
    - Fill in:
        - Protocol = 00
        - TOS = 0xFC (DSCP 63)
    - Select interface `ens1f1`
    - Send packet
- When you're done, remove the rerouting and re-add the default case:

    ```
    python send_usecase.py remove 3
    python send_usecase.py add 0
    ```
## Use-case 4: Alternative route
This use case is meant to be used in combination with [Default connection](#default-connection), and provides a direct optical path between TOR1 and TOR3, like so:    <br/>
CN1 -> TOR1 -> Polatis -> TOR3 -> CN3 (DSCP)

- Add the flows to ODL.  On the controller node:

    ``` 
    cd tue_tor/OfdPy/examples/IBM_ECOC
    python send_usecase.py send 2
    ```

# Debugging tools:
- To see hardware counters, in the switch:

    ```
    ./client_drivshell show c
    ```

- To see port status, in the switch:

    ```
    ./client_drivshell ps
    ```

- To poll flow inventory in ODL, on the controller node:

    ```
    curl -u admin:admin http://10.10.10.254:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:5593[0-2] | json_pp
    ```

- To force-delete flows in ODL, on the controller node:

    ```
    curl -X DELETE -u admin:admin http://10.10.10.254:8181/restconf/config/opendaylight-inventory:nodes/node/openflow:5593[0-2]/table/[10,50,60]
    ```

- To see optical paths in the Polatis switch:

    ```
    curl -u admin:admin http://10.10.10.254:8181/restconf/config/opendaylight-optical-provisioning-manager:nodes/node/openflow:1837 | json_pp
    ```
