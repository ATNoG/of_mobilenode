# of_mobilenode
OpenFlow within the Mobile Node (OFMN) implements flow mobility on the end nodes through OpenFlow tools (namely, Open vSwitch (OvS) and Pox Controller). 

## Code reuse

If you plan to reuse any of the available code, please consider to cite the following papers:

- F. Meneses, D. Corujo, C. Guimarães, R. Aguiar, "Extending SDN to End Nodes Towards Heterogeneous Wireless Mobility", IEEE WS SDRANCAN (IEEE Globecom WS),USA, Dec 2015

- F. Meneses, D. Corujo, C. Guimarães, R. Aguiar, "Multiple Flow in Extended SDN Wireless Mobility, European Workshop on Software Defined Networks", Spain, Aug 2015


## System framework
The framework was designed to work on 6 nodes (one for each emulated network node) of the AMazING tested, sited in the rooftop of Instituto de Telecomunicações de Aveiro.
Each node is composed by a VIA Eden 1GHz processor with 1GB RAM and two wireless interfaces (an 802.11a/b/g/n Atheros 9K and a 802.11a/b/g Atheros 5K), running Ubuntu 12.04 LTS.

## Open vSwitch installation
Since we do not change the OvS software you can check out how to install the sofware on developers [github](https://github.com/openvswitch/ovs).

## Requirements to run POX
POX officially requires Python 2.7, and should run under Linux, Mac OS, and Windows.

### Usage
The script ext/handover_mn.py handles the Mobile Node handover request. Run it along with l3_learning

* You can run with the "py" component and use the CLI:

  ./pox.py forwarding.l3_learning handover_demo1a py


## Get more information
For more information check the project's [webpage](http://atnog.github.io/of_mobilenode/index.html), and/or the [documentation](https://github.com/ATNoG/of_mobilenode/wiki) for experiments configuration and reproducibility tips.
