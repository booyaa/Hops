"""
Bot
"""

import logging

# import argparse
import copy
from typing import Optional
from .client import Client
from .storage import Storage
from .message_coordinates import MessageCoordinates
from .util import get_or_else


class Hops:
    """
    Handler for messages which will be parsed as commands with an attempt being made
    to execute the command if possible with replies going back to the `client`.
    """

    prefix = "."

    synonyms = {
        "👋": "hello",
        "👋🏻": "hello",
        "👋🏼": "hello",
        "👋🏽": "hello",
        "👋🏾": "hello",
        "👋🏿": "hello",
        "info": "help",
        "?": "help",
        "!": "help",
        "🤨": "help",
    }

    def __init__(self, storage: Optional[Storage] = None):
        """
        Initialize the Hops instance with optional storage.
        """
        self.storage = storage

    def on_message(
        self, coordinates: MessageCoordinates, message: str, client: Client
    ) -> None:
        """
        Handler for incoming messages
        """

        if self.storage is not None:
            self.storage.log_received(
                coordinates.from_id, coordinates.channel_index, message
            )

        split = message.split(" ", 1)

        command = split[0]

        # Require that the command be prefixed with by '.'
        if not command.startswith(self.prefix):
            return
        command = command[1:]

        # Map synonyms to canonical names
        command = self.synonyms[command] if command in self.synonyms else command

        method_name = f"_on_{command.lower()}"
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                arguments = split[1] if len(split) > 1 else None
                logging.debug("Received %s", command)
                method(coordinates, arguments, client)

    def _on_hello(
        self, coordinates: MessageCoordinates, _argument: str, client: Client
    ) -> None:
        """
        Say hello
        """
        client.send_response(
            message="👋",
            message_coordinates=coordinates,
        )

    def _on_ping(
        self, coordinates: MessageCoordinates, _argument: str, client: Client
    ) -> None:
        """
        Respond to a ping
        """
        client.send_response(
            message="🏓",
            message_coordinates=coordinates,
        )

    def _on_help(
        self, coordinates: MessageCoordinates, _argument: str, client: Client
    ) -> None:
        """
        Provide help info
        """
        client.send_response(
            message="http://w2asm.com/hops",
            message_coordinates=coordinates,
        )

    def _on_post(self, coordinates: MessageCoordinates, argument: str, client: Client):
        if self.storage is None:
            logging.info("Cannot use BBS without storage")
            return

        self.storage.bbs_insert(
            from_id=coordinates.from_id,
            from_short_name=get_or_else(
                coordinates, ["from_node", "user", "shortName"]
            ),
            from_long_name=get_or_else(coordinates, ["from_node", "user", "longName"]),
            message=argument,
        )
        client.send_response(message="💾", message_coordinates=coordinates)

    def _on_bbs(self, coordinates: MessageCoordinates, _argument: str, client: Client):
        if self.storage is None:
            logging.info("Cannot use BBS without storage")
            return

        if not coordinates.is_dm:
            client.send_response(
                message="🚫 Only allowed in DM", message_coordinates=coordinates
            )
            return

        new_coordinates = copy.deepcopy(coordinates)
        new_coordinates.is_dm = True
        new_coordinates.message_id = None

        rows = self.storage.bbs_read()

        messages = []
        for row in rows[0:5]:
            from_id = (
                row["from_short_name"]
                if row["from_short_name"] is not None
                else row["from_id"]
            )
            messages.append(f"{from_id}: {row['message']}")

        # Group the messages together into as few messages as possible
        concatenated_messages = []
        current_message = ""
        for message in messages:
            if len(current_message) + len(message) + 1 <= 200:
                current_message += f"\n{message}"
            else:
                concatenated_messages.append(current_message)
                current_message = message

        if current_message:
            concatenated_messages.append(current_message)

        for message in concatenated_messages:
            client.send_response(message=message, message_coordinates=new_coordinates)
