# of_mobilenode
This project mains to implement a flow mobility on the end nodes through OpenFlow tools. To accomplish that OpenFlow agents Open vSwitch and POX were used to perform the flow mobility.

## System framework
The framework was design to work on 6 nodes (one for each emulated network node) of the AMazING tested, sited in the rooftop of Instituto de Telecomunicações de Aveiro.
Each node is composed by a VIA Eden 1GHz processor with 1GB RAM and two wireless interfaces (an 802.11a/b/g/n Atheros 9K and a 802.11a/b/g Atheros 5K), running Ubuntu 12.04 LTS.

## Open vSwitch installation
Since we do not change the OvS software you can check out how to install the sofware on developers [github](https://github.com/openvswitch/ovs).

## Requirements to run POX
POX officially requires Python 2.7 (though much of it will work fine fine with Python 2.6), and should run under Linux, Mac OS, and Windows.

### Usage
The script ext/handover_demo1a.py handles the Mobile Node handover request. Run it along with l3_learning

* You can run with the "py" component and use the CLI:

  ./pox.py forwarding.l3_learning handover_demo1a py


# Experience example
Check the more information about how to configure and reproduce the experience on the [documentation](http://atnog.github.io/of_mobilenode/index.html).
