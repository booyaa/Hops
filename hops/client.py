"""
This module provides the `Hops` class, which serves as an interface for
interacting with a Meshtastic network via a TCP connection. The class utilizes
the `pubsub` library to subscribe to various Meshtastic events and provides
callback methods to handle these events, such as connection establishment, data
reception, node updates, position updates, text messages, and user updates.
"""

import sys
import logging
import emoji
from pubsub import pub
import meshtastic
from meshtastic.stream_interface import StreamInterface
from meshtastic.protobuf.mesh_pb2 import Data, MeshPacket
from meshtastic.protobuf.portnums_pb2 import PortNum
from .util import get_or_else
from .message_coordinates import MessageCoordinates


class Client:
    """
    Meshtastic bot
    """

    def __init__(self, interface: StreamInterface, hops):
        self.interface = interface
        self.hops = hops
        self.me = {}
        self.nodes = {}
        pub.subscribe(self._event_connect, "meshtastic.connection.established")
        pub.subscribe(self._event_disconnect, "meshtastic.connection.lost")
        pub.subscribe(self._event_text, "meshtastic.receive.text")

    def send_response(self, message: str, message_coordinates: MessageCoordinates):
        """
        Send a message
        """

        is_emoji = len(message) == 1 and message in emoji.EMOJI_DATA

        data_packet = Data(
            portnum=PortNum.TEXT_MESSAGE_APP,
            payload=message.encode("utf-8"),
            emoji=is_emoji,
            want_response=False,
        )
        if message_coordinates.message_id is not None:
            data_packet.reply_id = message_coordinates.message_id

        mesh_packet = MeshPacket(
            channel=(
                message_coordinates.channel_index
                if message_coordinates.channel_index is not None
                else 0
            ),
            decoded=data_packet,
            id=self.interface._generatePacketId(),
            priority=MeshPacket.Priority.RELIABLE,
        )

        destination_id = meshtastic.BROADCAST_ADDR
        if message_coordinates.is_dm:
            destination_id = message_coordinates.from_id

        self.interface._sendPacket(
            mesh_packet,
            destinationId=destination_id,
            wantAck=False,
            hopLimit=3,
            pkiEncrypted=False,
            publicKey=None,
        )

    def _event_connect(self, interface: StreamInterface) -> None:
        """
        Callback function for connection established
        """
        # Suppress unused error
        _ = interface
        logging.info("Connected")

    def _event_disconnect(
        self, interface: StreamInterface, topic=pub.AUTO_TOPIC
    ) -> None:
        """
        Callback function for connection lost
        """
        # Suppress unused error
        _ = interface
        _ = topic
        logging.warning("Lost connection to radio!")
        sys.exit()

    def _event_text(self, packet: dict, interface: StreamInterface) -> None:
        """
        Callback function for received packets
        """
        # Suppress unused error
        _ = interface

        coordinates = MessageCoordinates.from_packet(packet, self.interface)
        message = get_or_else(packet, ["decoded", "payload"], "").decode("utf-8")
        self.hops.on_message(coordinates, message, self)
