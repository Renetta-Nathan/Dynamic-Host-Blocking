from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, CONFIG_DISPATCHER, set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet, ethernet


class DynamicBlock(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(DynamicBlock, self).__init__(*args, **kwargs)
        self.mac_to_port = {}
        self.packet_count = {}
        self.threshold = 20   # change this for sensitivity

    # 🔹 Install default rule
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER)]

        self.add_flow(datapath, 0, match, actions)

    # 🔹 Function to add flow
    def add_flow(self, datapath, priority, match, actions, idle_timeout=0):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]

        mod = parser.OFPFlowMod(
            datapath=datapath,
            priority=priority,
            match=match,
            instructions=inst,
            idle_timeout=idle_timeout
        )
        datapath.send_msg(mod)

    # 🔹 Packet processing
    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        parser = datapath.ofproto_parser
        ofproto = datapath.ofproto

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == 35020:  # ignore LLDP
            return

        src = eth.src
        dst = eth.dst
        dpid = datapath.id
        in_port = msg.match['in_port']

        # 🔢 Count packets per source
        self.packet_count[src] = self.packet_count.get(src, 0) + 1

        # 🚨 BLOCK if threshold exceeded
        if self.packet_count[src] > self.threshold:
            self.logger.info(f"🚫 Blocking host: {src}")

            match = parser.OFPMatch(eth_src=src)
            actions = []  # DROP

            self.add_flow(datapath, 100, match, actions, idle_timeout=30)
            return

        # 📚 Learning switch logic
        self.mac_to_port.setdefault(dpid, {})
        self.mac_to_port[dpid][src] = in_port

        out_port = self.mac_to_port[dpid].get(dst, ofproto.OFPP_FLOOD)
        actions = [parser.OFPActionOutput(out_port)]

        match = parser.OFPMatch(eth_dst=dst)

        if out_port != ofproto.OFPP_FLOOD:
            self.add_flow(datapath, 1, match, actions, idle_timeout=30)

        out = parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=msg.data
        )
        datapath.send_msg(out)