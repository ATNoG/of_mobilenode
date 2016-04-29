#!/usr/bin/python
"""
Add flows to MN perfom handover

MN 1 - attached to AP1 (ath1) and AP2 (ath0)
MN 2 - attached to AP3 (ath1) and AP2 (ath0)

Scenario: Handover triggered by AP2 through PacketIn message

Save as ext/handover.py and run along with l3_learning.

Alternatively, if you run with the "py" component, you can use the CLI:
./pox.py forwarding.l3_learning handover py

To start in debug level, you can use the CLI:
./pox.py log.level --DEBUG forwarding.l3_learning handover py

 ...
POX> 
"""
from pox.core import core
import pox.openflow.libopenflow_01 as of
import pox.lib.packet as pkt
from pox.lib.util import dpid_to_str
from pox.lib.revent import *
from pox.openflow.of_json import *
from datetime import datetime
from pox.lib.recoco import Timer

log = core.getLogger()

scenario=0

# Global variables
firstTime1=True
firstTime2=True
handover_mn1=False
old_byte_count1=0
old_byte_count2=0

iperf_dst_port=5001 #iperf
vlc_dst_port=5004 #video
tcp_dst_port=9991 #data

mn1_br0_dpid=0
mn1_br1_dpid=0
mn2_br0_dpid=0
mn2_br1_dpid=0

ap1_dpid=0
ap2_dpid=0
ap3_dpid=0

barrier_xid_mn1=0
barrier_xid_mn2=0

patchPort_n_mn1=2
patchPort_n_mn2=2

# Mobile node ath interfaces
mn1_ath0="00:80:48:62:e7:e4"
mn1_ath1="00:80:48:62:4e:7c"
mn2_ath0="00:80:48:62:e7:d9"
mn2_ath1="00:80:48:5f:a2:87"

mn1_ath0_ip="192.168.12.1"
mn1_ath1_ip="192.168.11.1"
mn2_ath0_ip="192.168.12.2"
mn2_ath1_ip="192.168.13.2"
listener_ip="192.168.10.1"

#AP eth interfaces
ap1_eth="00:11:11:11:11:22"
ap2_eth="00:22:22:22:22:33"
ap3_eth="00:33:33:33:33:44"

# APs ath interfaces
ap1_ath="00:80:48:62:4e:78"
ap2_ath="00:80:48:62:4e:83"
ap3_ath="00:80:48:62:4e:80"

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

class MyConnection(object):
  def __init__(self):
    core.openflow.addListeners(self)

  def _handle_ConnectionUp(self,event):
    ConnectionUp(event.connection,event.ofp)
    global mn1_br0_dpid
    global mn1_br1_dpid
    global mn2_br0_dpid
    global mn2_br1_dpid
    global ap1_dpid
    global ap2_dpid
    global ap3_dpid

    for m in event.connection.features.ports:
      # Mobile Node 1
      if m.name == "ath0" and str(m.hw_addr) == str(mn1_ath0):
        mn1_br0_dpid = event.connection.dpid
        log.debug("[ mn1_br0_dpid = %s ] UP", dpid_to_str(mn1_br0_dpid))
      elif m.name == "ath1" and str(m.hw_addr) == str(mn1_ath1):
        mn1_br1_dpid = event.connection.dpid
        log.debug("[ mn1_br1_dpid = %s ] UP", dpid_to_str(mn1_br1_dpid))

      # Mobile Node 2
      elif m.name == "ath0" and str(m.hw_addr) == str(mn2_ath0):
        mn2_br0_dpid = event.connection.dpid
        log.debug("[ mn2_br0_dpid = %s ] UP", dpid_to_str(mn2_br0_dpid))
      elif m.name == "ath1" and str(m.hw_addr) == str(mn2_ath1):
        mn2_br1_dpid = event.connection.dpid
        log.debug("[ mn2_br1_dpid = %s ] UP", dpid_to_str(mn2_br1_dpid))

      # APs
      elif m.name == "ap1" and str(m.hw_addr) == str(ap1_eth):
        ap1_dpid = event.connection.dpid
        log.debug("[ AP1_dpid = %s ] UP", dpid_to_str(ap1_dpid))
        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_NORMAL ), 
          priority=1 ))

      elif m.name == "ap2" and str(m.hw_addr) == str(ap2_eth):
        ap2_dpid = event.connection.dpid
        log.debug("[ AP2_dpid = %s ] UP", dpid_to_str(ap2_dpid))
        # add flow rules
        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_NORMAL ), 
          priority=1 ))

        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_CONTROLLER ), 
          priority=100, match=of.ofp_match( dl_type=0x800, nw_dst="33.33.33.33/32" )))

        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_NORMAL), 
          priority=10,  match=of.ofp_match( dl_type=0x800, nw_src=mn1_ath0_ip, 
            nw_dst=listener_ip, nw_proto = pkt.ipv4.TCP_PROTOCOL, tp_dst=tcp_dst_port)))

        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_NORMAL),
          priority=10, match=of.ofp_match( dl_type=0x800, nw_src=mn1_ath0_ip, 
            nw_dst=listener_ip, nw_proto = pkt.ipv4.UDP_PROTOCOL, tp_dst=vlc_dst_port)))

        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_NORMAL),
          priority=10, match=of.ofp_match( dl_type=0x800, nw_src=mn2_ath0_ip, 
            nw_dst=listener_ip, nw_proto = pkt.ipv4.TCP_PROTOCOL, tp_dst=tcp_dst_port)))

        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_NORMAL),
          priority=10, match=of.ofp_match( dl_type=0x800, nw_src=mn2_ath0_ip, 
            nw_dst=listener_ip, nw_proto = pkt.ipv4.UDP_PROTOCOL, tp_dst=vlc_dst_port)))

      elif m.name == "ap3" and str(m.hw_addr) == str(ap3_eth):
        ap3_dpid = event.connection.dpid
        log.debug("[ AP3_dpid = %s ] UP", dpid_to_str(ap3_dpid))
        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_NORMAL ), 
          priority=1 ))      

      else:
        event.connection.send( of.ofp_flow_mod( action=of.ofp_action_output( port=of.OFPP_NORMAL ), 
          priority=1 ))

  def _handle_ConnectionDown(self,event):
    ConnectionDown(event.connection,event.dpid)
    log.debug("Switch %s DOWN.",dpid_to_str(event.dpid))

class MyFlow(object):
  def __init__(self):
    core.openflow.addListeners(self)
  def _handle_PacketIn(self,event):
    global handover_mn1
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

      if dst_ip == "11.11.11.11":
        # flow MN1 > AP1
        flow_patch2port(True,False)
      if dst_ip == "22.22.22.22":
        # Flow MN2 > AP3
        flow_patch2port(False,True)
      if dst_ip == "33.33.33.33":
        # AP2 handover trigger
        if handover_mn1 is False:
          handover_mn1 = True
          flow_patch2port(True,False)
        else:
          flow_patch2port(False,True)

  def _handle_BarrierIn(self,event):
    if event.ofp.xid == barrier_xid_mn1:
      # flow to MN-1 br0 > br1
      flow_port2pacth(True, False, False)

    elif event.ofp.xid == barrier_xid_mn2:
      # flow to MN_2 br0 > br1
      flow_port2pacth(False, True, False)

    else:
      return

    self.nexus = None

def flow_patch2port (mn1,mn2):
  global barrier_xid_mn1
  global barrier_xid_mn2
  log.info(" Start adding flow at: %s", str(datetime.now()))
  msg1 = of.ofp_flow_mod()
  msg1.priority = 100
  msg1.match.dl_type = 0x800
  msg1.match.nw_dst = listener_ip
  msg1.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
  msg1.match.tp_dst = iperf_dst_port
  #msg1.match.tp_dst = vlc_dst_port
  
  if mn1:
    msg1.match.in_port = patchPort_n_mn1
    msg1.actions.append(of.ofp_action_dl_addr.set_src(dl_addr=mn1_ath1))
    msg1.actions.append(of.ofp_action_dl_addr.set_dst(dl_addr=ap1_ath))
    msg1.actions.append(of.ofp_action_output(port = 1))
    dpid_1 = mn1_br1_dpid

  elif mn2:
    msg1.match.in_port = patchPort_n_mn2
    msg1.actions.append(of.ofp_action_dl_addr.set_src(dl_addr=mn2_ath1))
    msg1.actions.append(of.ofp_action_dl_addr.set_dst(dl_addr=ap3_ath))
    msg1.actions.append(of.ofp_action_output(port = 1))
    dpid_1 = mn2_br1_dpid

  else:
    return

  # pre-handover (patch -> athX)
  core.openflow.sendToDPID(dpid_1,msg1)
  log.debug("[ Flow for br1: %s ] at [ %s ]", dpid_to_str(dpid_1),str(datetime.now()))
  
  #Make sure that 1st flow_mod was implemented
  b=of.ofp_barrier_request()
  if mn1:
    barrier_xid_mn1=b.xid
  elif mn2:
    barrier_xid_mn2=b.xid
  else:
    return

  core.openflow.sendToDPID(dpid_1,b)
  log.debug("Sent Barrier at: %s", str(datetime.now()))

def flow_port2pacth(mn1,mn2,rm):
  log.debug("Sent FLOW_MOD 2 at: %s", str(datetime.now()))

  # all nw_dst -> patch
  msg0 = of.ofp_flow_mod()
  msg0.priority = 100
  msg0.match.dl_type = 0x800
  msg0.match.nw_dst = listener_ip
  msg0.match.nw_proto = pkt.ipv4.UDP_PROTOCOL
  msg0.match.tp_dst = iperf_dst_port

  if mn1:
    msg0.actions.append(of.ofp_action_output(port = patchPort_n_mn1))
    dpid_0 = mn1_br0_dpid

  elif mn2:
    msg0.actions.append(of.ofp_action_output(port = patchPort_n_mn2))
    dpid_0 = mn2_br0_dpid

  else:
    return
    
  if rm:
    # remove redirect flow from br0
    msg0.actions.append(of.OFPFC_DELETE_STRICT)

  core.openflow.sendToDPID(dpid_0,msg0) 
  log.info(" Ended adding flow at: %s", str(datetime.now()))

def launch():
  core.registerNew(MyConnection)
  core.registerNew(MyFlow)