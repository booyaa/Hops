"""
This module provides the `Hops` class, which serves as an interface for
interacting with a Meshtastic network via a TCP connection. The class utilizes
the `pubsub` library to subscribe to various Meshtastic events and provides
callback methods to handle these events, such as connection establishment, data
reception, node updates, position updates, text messages, and user updates.
"""
import logging
from typing import Union
from pubsub import pub
import meshtastic
from meshtastic.stream_interface import StreamInterface
# from meshtastic.protobuf import portnums_pb2
from .util import get_or_else
# from .hops import Hops

class Client:
    """
    Meshtastic bot
    """
    def __init__(self, interface: StreamInterface, hops):
        self.interface = interface
        self.hops = hops
        self.me = {}
        self.nodes = {}

        pub.subscribe(self._event_connect,    'meshtastic.connection.established')
        pub.subscribe(self._event_data,       'meshtastic.receive.data.portnum')
        pub.subscribe(self._event_disconnect, 'meshtastic.connection.lost')
        pub.subscribe(self._event_node,       'meshtastic.node')
        pub.subscribe(self._event_position,   'meshtastic.receive.position')
        pub.subscribe(self._event_text,       'meshtastic.receive.text')
        pub.subscribe(self._event_user,       'meshtastic.receive.user')

    def send_text(
        self,
        text: str,
        destination_id: Union[int, str] = meshtastic.BROADCAST_ADDR,
        channel_index: int = 0,
        # port_num: portnums_pb2.P8ortNum.ValueType = portnums_pb2.PortNum.TEXT_MESSAGE_APP
    ):
        """
        Send a message
        """

        port_num = 0

        self.interface.sendText(
            text,
            destination_id,
            wantAck = False,
            wantResponse = False,
            onResponse = None,
            channelIndex = channel_index,
            portNum = port_num,
        )

    def _event_connect(self, _interface, _topic=pub.AUTO_TOPIC):
        '''
        Callback function for connection established

        :param interface: Meshtastic interface
        :param topic:     PubSub topic
        '''
        logging.info(
            'Connected to the %s radio on %s hardware',
            self.me["user"]["longName"],
            self.me["user"]["hwModel"]
        )

    def _event_data(self, packet: dict, _interface):
        '''
        Callback function for data updates

        :param packet: Data information
        :param interface: Meshtastic interface
        '''
        logging.info('Data update: %s', packet)

    def _event_disconnect(self, _interface, _topic=pub.AUTO_TOPIC):
        '''
        Callback function for connection lost

        :param interface: Meshtastic interface
        :param topic:     PubSub topic
        '''
        logging.warning('Lost connection to radio!')
        exit()


    def _event_node(self, node):
        '''
        Callback function for node updates

        :param node: Node information
        '''

    def _event_position(self, packet: dict, interface):
        '''
        Callback function for position updates

        :param packet: Position information
        :param interface: Meshtastic interface
        '''
        # sender = get_or_else(packet, ['from'])
        # msg = get_or_else(packet, ['decoded', 'payload'], '').hex()
        # sender_id = get_or_else(self.nodes[sender], ['user', 'id']) if sender in self.nodes else '!unk'
        # name = get_or_else(self.nodes[sender], ['user', 'longName']) if sender in self.nodes else 'UNK'
        # longitude = get_or_else(packet, ['decoded', 'position', 'longitudeI'], 0) / 1e7
        # latitude = get_or_else(packet, ['decoded', 'position', 'latitudeI'], 0) / 1e7
        # altitude = get_or_else(packet, ['decoded', 'position', 'altitude'])
        # snr = get_or_else(packet, ['rxSnr'])
        # rssi = get_or_else(packet, ['rxRssi'])

    def _event_text(self, packet: dict, _interface):
        '''
        Callback function for received packets

        :param packet: Packet received
        '''

        sender = get_or_else(packet, ['from'])
        to = get_or_else(packet, ['to'])
        msg = get_or_else(packet, ['decoded', 'payload'], '').decode('utf-8')
        # sender_id = get_or_else(self.nodes[sender], ['user', 'id']) if sender in self.nodes else '!unk'
        # channel_id = get_or_else(packet, ['channel'])

        self.hops.on_message(sender, to, msg, self)


    def _event_user(self, packet: dict, interface):
        '''
        Callback function for user updates

        :param user: User information
        '''
