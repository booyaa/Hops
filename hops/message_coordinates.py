"""
Represents message coordinates in a communication system.
    from_id (Union[int, str]): Sender ID.
    from_node (Optional[dict]): Sender node details.
    to_id (Optional[Union[int, str]]): Receiver ID.
    to_node (Optional[dict]): Receiver node details.
    message_id (int): Message unique identifier.
    channel_index (Optional[int]): Channel index.
Methods:
    from_packet(packet: dict, interface: StreamInterface) -> "Coordinates":
        Creates an instance from a packet dictionary.
"""

# import logging
from typing import Union
from typing import Optional
from meshtastic.stream_interface import StreamInterface
from .util import get_or_else


class MessageCoordinates:
    """
    Represents the coordinates of a message in a communication system, including
    details about the sender, receiver, message ID, and channel information.
    """

    def __init__(
        self,
        from_id: Union[int, str],
        from_node: Optional[dict],
        to_id: Optional[Union[int, str]],
        to_node: Optional[dict],
        message_id: int,
        channel_index: Optional[int],
        is_dm: bool,
    ):
        self.from_id = from_id
        self.from_node = from_node
        self.to_id = to_id
        self.to_node = to_node
        self.message_id = message_id
        self.channel_index = channel_index
        self.is_dm = is_dm

    @staticmethod
    def from_packet(packet: dict, interface: StreamInterface) -> "MessageCoordinates":
        """
        Create a Coordinates instance from a packet dictionary.

        :param packet: Packet dictionary containing message details.
        :return: Coordinates instance.
        """
        from_id = get_or_else(packet, ["from"])
        to_id = get_or_else(packet, ["to"])
        message_id = get_or_else(packet, ["id"])
        channel_index = get_or_else(packet, ["channel"], None)

        from_node = interface.nodes[from_id] if from_id in interface.nodes else None
        to_node = interface.nodes[to_id] if to_id in interface.nodes else None

        is_dm = to_id == interface.myInfo.my_node_num

        return MessageCoordinates(
            from_id,
            from_node,
            to_id,
            to_node,
            message_id,
            channel_index,
            is_dm,
        )
