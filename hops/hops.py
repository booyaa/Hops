"""
Bot
"""

import logging
import argparse
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
            message="ack",
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

    def _on_bbs(self, coordinates: MessageCoordinates, argument: str, client: Client):
        parser = argparse.ArgumentParser(description="Bulletin Board System")
        parser.add_argument("command", choices=["help", "add"], nargs="?", default=None)
        parser.add_argument("message", nargs=argparse.REMAINDER)
        args = parser.parse_args(argument.split() if argument else [])

        if args.command == "help":
            client.send_response(
                message="http://w2asm.com/hops/bbs/",
                message_coordinates=coordinates,
            )
            return

        if self.storage is None:
            logging.info("Cannot use BBS without storage")
            return

        if args.command == "add":
            message = " ".join(args.message if args.message is not None else [])
            self.storage.bbs_insert(
                from_id=coordinates.from_id,
                from_short_name=get_or_else(
                    coordinates, ["from_node", "user", "shortName"]
                ),
                from_long_name=get_or_else(
                    coordinates, ["from_node", "user", "longName"]
                ),
                channel_index=coordinates.channel_index,
                message=message,
            )
            return

        rows = self.storage.bbs_read(
            channel_index=coordinates.channel_index,
        )

        for row in rows[0:5]:
            from_id = (
                row["from_short_name"]
                if row["from_short_name"] is not None
                else row["from_id"]
            )
            message = f"{from_id}: {row['message']}"
            client.send_response(message=message, message_coordinates=coordinates)
