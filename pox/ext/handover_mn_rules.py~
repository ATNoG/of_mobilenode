#!/usr/bin/python
"""
Add flows to MN and router
 
Save as ext/handover.py and run along with l3_learning.
  
Alternatively, if you run with the "py" component, you can use the CLI:
./pox.py forwarding.l3_learning handover py
 ...
POX> add_flow_mn() OR add_flow_router()
"""
from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str
from pox.lib.revent import *
from datetime import datetime

log = core.getLogger()
mn_br0_dpid=0
mn_br1_dpid=0
router_dpid=0
barrier_xid=0

class ConnectionUp(Event):
    def __init__(self,connection,ofp):
        Event.__init__(self)
        self.connection = connection
        self.dpid = connection.dpid
        self.ofp = ofp

class ConnectionDown(Event):
    def __init__(self,connection,ofp):
        Event.__init__(self)
        self.connection = connection
        self.dpid = connection.dpid

class PacketIn(Event):
    def __init__(self,connection,ofp):
        Event.__init__(self)
        self.connection = connection
        self.dpid = connection.dpid

class MyConnection(object):
    def __init__(self):
        core.openflow.addListeners(self)

    def _handle_ConnectionUp(self,event):
        ConnectionUp(event.connection,event.ofp)
	global mn_br0_dpid
	global mn_br1_dpid
        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_NORMAL ), priority=1 ))
  	for m in event.connection.features.ports:
   	 if m.name == "patch01":
	  print "-------------"
    	  mn_br0_dpid = event.connection.dpid
    	  log.info("[ mn_br0_dpid = %s ] UP", dpid_to_str(mn_br0_dpid))
          #log.info(dpid_to_str(event.dpid))
	  print "-------------"
         if m.name == "patch10":
          print "-------------"
    	  mn_br1_dpid = event.connection.dpid
    	  log.info("[ mn_br1_dpid = %s ] UP", dpid_to_str(mn_br1_dpid))
	  #log.info(dpid_to_str(event.dpid)) 
	  print "-------------"       

    def _handle_ConnectionDown(self,event):
        ConnectionDown(event.connection,event.dpid)
        log.info("Switch %s DOWN.",dpid_to_str(event.dpid))

class MyFlow(object):
    def __init__(self):
        core.openflow.addListeners(self)
    def _handle_PacketIn(self,event):
	PacketIn(event.connection,event.ofp)
	packet_in = event.ofp
	packet = event.parsed
	src_mac = packet.src
	dst_mac = packet.dst
	if packet.type == of.ethernet.IP_TYPE:
	    ipv4_packet = event.parsed.find("ipv4")
	    # Do more processing of the IPv4 packet
	    src_ip = ipv4_packet.srcip
	    dst_ip = ipv4_packet.dstip
	match = of.ofp_match.from_packet(packet)
        log.info("[ Packet_in from: %s ",dpid_to_str(event.dpid))
        log.info("  src_ip: %s ",src_ip)
        log.info("  dst_ip: %s ]",dst_ip)
  	print "start dummy rules!: ", str(datetime.now())
	for R in range(1, 10000):
	    if "9999" == "%d" % (R):
		print "last round"
	    if dst_ip == "11.11.10.99":
		print "------- Dummy rule detected! --------"
	if dst_ip == "11.11.11.11":
	  flow_mn_2()

    def _handle_BarrierIn(self,event):
	if event.ofp.xid != barrier_xid:
	  return
  
	# MN.br1 (all nw_dst -> patch)
  	msg1 = of.ofp_flow_mod()
  	msg1.priority = 100
  	msg1.match.dl_type = 0x800
  	msg1.match.nw_dst = "192.168.10.1"
 	msg1.actions.append(of.ofp_action_output(port = 3))
  	core.openflow.sendToDPID(mn_br0_dpid,msg1)
	print "FLOW_MOD 2: %s", str(datetime.now())
  	print "----End add flow-----"

	self.nexus = None

def flow_mn_2 ():
  global barrier_xid
  print "-----Start add flow---- %s", str(datetime.now())
  log.info("[ mn_br0_dpid = %s ] UP", dpid_to_str(mn_br0_dpid))
  log.info("[ mn_br1_dpid = %s ] UP", dpid_to_str(mn_br1_dpid))
  # MN.br0 (patch -> ath1)
  msg0 = of.ofp_flow_mod()
  msg0.priority = 100
  msg0.match.in_port = 3
  msg0.match.dl_type = 0x800
  msg0.match.nw_dst = "192.168.10.1"
  msg0.actions.append(of.ofp_action_dl_addr.set_src(dl_addr="00:80:48:62:4e:7c"))
  msg0.actions.append(of.ofp_action_dl_addr.set_dst(dl_addr="00:80:48:62:4e:78"))
  msg0.actions.append(of.ofp_action_output(port = 1))
  core.openflow.sendToDPID(mn_br1_dpid,msg0)
  print "FLOW_MOD 1: %s", str(datetime.now())
  #Make sure that 1st flow_mod was implemented
  b=of.ofp_barrier_request()
  barrier_xid=b.xid
  core.openflow.sendToDPID(mn_br1_dpid,b)
  print "BARRIER: %s", str(datetime.now())

def launch():
    core.registerNew(MyConnection)
    core.registerNew(MyFlow)
