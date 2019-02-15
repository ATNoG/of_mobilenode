# OFMN - OpenFlow within MN
This project mains to implement a flow mobility on the end nodes through OpenFlow tools. To accomplish that OpenFlow agents Open vSwitch and POX were used to perform the flow mobility.

## Open vSwitch installation
Since we do not change the OvS software you can check out how to install the sofware on the developers webpage [github](https://github.com/openvswitch/ovs).

## Requirements to run POX
POX officially requires Python 2.7 (though much of it will work fine fine with Python 2.6), and should run under Linux, Mac OS, and Windows.

### Usage
The script ext/handover_demo1a.py handles the Mobile Node handover request. Run it along with l3_learning

* You can run with the "py" component and use the CLI:

  ./pox.py forwarding.l3_learning handover_demo1a py


# Experience example
Check the more information about how to configure and reproduce the experience on the [documentation](https://github.com/ATNoG/of_mobilenode/wiki).
