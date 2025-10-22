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
from .util import get_or_else, num_to_id

import os
import subprocess

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
        "🏓": "ping",
        ".": "ping",
        "mail": "messages",
    }

    # get value from environment variable HOPS_ADMIN_ID
    admin_user_id = None
    if "HOPS_ADMIN_ID" in os.environ:
        try:
            admin_user_id = os.environ["HOPS_ADMIN_ID"]
            test_as_valid_node_num = int(admin_user_id.replace("!",""), 16)
        except ValueError:
            logging.warning("HOPS_ADMIN_ID is missing or invalid")

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
            message="https://github.com/booyaa/Hops/blob/main/HELP.md",
            message_coordinates=coordinates,
        )

    def _on_whoami(
        self, coordinates: MessageCoordinates, argument: str, client: Client
    ):
        _ = argument
        components = []
        components.append(num_to_id(coordinates.from_id))
        if coordinates.from_node is not None:
            components.append(
                " ".join(
                    [
                        get_or_else(
                            coordinates.from_node,
                            ["user", "shortName"],
                            "Unknown short",
                        ),
                        get_or_else(
                            coordinates.from_node, ["user", "longName"], "Unknown long"
                        ),
                    ]
                )
            )
        components.append(f'snr: {get_or_else(coordinates.from_node, ["snr"])}')
        components.append(f'hops: {get_or_else(coordinates.from_node, ["hops"])}')
        client.send_response(
            message="\n".join(components),
            message_coordinates=coordinates,
        )

    def _on_status(self, coordinates: MessageCoordinates, argument: str, client: Client):
        _ = argument
        components = []

        if self.admin_user_id is None or num_to_id(coordinates.from_id) != self.admin_user_id:
            logging.warning("Unauthorized status request from %s", coordinates.from_id)
            return

        uptime = subprocess.check_output(["uptime", "-p"]).decode("utf-8").strip()
        components.append(f"uptime: {uptime}")

        ip_addresses = subprocess.check_output(["hostname", "-I"]).decode("utf-8").strip()
        ip_addresses = ip_addresses.split(" ")
        ip_address = ip_addresses[0] if len(ip_addresses) > 0 else "N/A"
        components.append(f"ip: {ip_address}")

        load_avg = subprocess.check_output(["cat", "/proc/loadavg"]).decode("utf-8").strip()
        load_avg = load_avg.split(" ")[0:3]
        load_avg = ", ".join(load_avg)
        components.append(f"load: {load_avg}")

        battery_info = subprocess.check_output(["./battery_meter"]).decode("utf-8").strip()
        components.append(f"battery: {battery_info} %")

        logging.info(components)
        # only send as DM
        new_coordinates = copy.deepcopy(coordinates)
        new_coordinates.is_dm = True
        new_coordinates.message_id = None

        client.send_response(
            message="\n".join(components),
            message_coordinates=new_coordinates,
        )

    def _on_shutdown(
        self, coordinates: MessageCoordinates, argument: str, client: Client
    ):
        _ = argument
        components = ["Shutting down..."]

        if self.admin_user_id is None or num_to_id(coordinates.from_id) != self.admin_user_id:
            logging.warning("Unauthorized shutdown request from %s", coordinates.from_id)
            return

        # only send as DM
        new_coordinates = copy.deepcopy(coordinates)
        new_coordinates.is_dm = True
        new_coordinates.message_id = None

        client.send_response(
            message="\n".join(components),
            message_coordinates=new_coordinates,
        )
        subprocess.Popen(["sudo", "shutdown", "-h", "now"])

    def _on_post(self, coordinates: MessageCoordinates, argument: str, client: Client):
        if self.storage is None:
            logging.info("Cannot use BBS without storage")
            return

        self.storage.bbs_insert(
            from_id=coordinates.from_id,
            from_short_name=get_or_else(coordinates.from_node, ["user", "shortName"]),
            from_long_name=get_or_else(coordinates.from_node, ["user", "longName"]),
            message=argument,
        )
        client.send_response(message="📤", message_coordinates=coordinates)

    def _on_bbs(self, coordinates: MessageCoordinates, _argument: str, client: Client):
        if self.storage is None:
            logging.info("Cannot use BBS without storage")
            return

        if not coordinates.is_dm:
            client.send_response(message="📬", message_coordinates=coordinates)

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
                current_message += f"\n{message}" if current_message else message
            else:
                concatenated_messages.append(current_message)
                current_message = message

        if current_message:
            concatenated_messages.append(current_message)

        for message in concatenated_messages:
            client.send_response(message=message, message_coordinates=new_coordinates)

    def _on_message(
        self, coordinates: MessageCoordinates, argument: str, client: Client
    ):
        if self.storage is None:
            logging.info("Cannot use Messages without storage")
            return

        split = argument.split(" ", 1)
        to_name = split[0]
        message = split[1] if len(split) > 1 else ""

        to_name = to_name.lower()
        to_id = None
        for node in client.interface.nodes.values():
            if "user" not in node:
                continue
            short = get_or_else(node["user"], ["shortName"])
            long = get_or_else(node["user"], ["longName"])
            if (short is not None and short.lower() == to_name) or (
                long is not None and long.lower() == to_name
            ):
                to_id = get_or_else(node["user"], ["id"])
                break

        if to_id is None:
            client.send_response(message="❌", message_coordinates=coordinates)
            return

        self.storage.messages_insert(
            from_id=coordinates.from_id,
            from_short_name=get_or_else(coordinates.from_node, ["user", "shortName"]),
            from_long_name=get_or_else(coordinates.from_node, ["user", "longName"]),
            to_id=to_id,
            message=message,
        )

        client.send_response(message="📤", message_coordinates=coordinates)

        # Notify the addressee
        addressee_coordinates = MessageCoordinates.from_addresses(
            to_id=to_id,
            from_id=num_to_id(client.interface.myInfo.my_node_num),
            channel_index=coordinates.channel_index,
            interface=client.interface,
        )
        client.send_response(message="📫", message_coordinates=addressee_coordinates)

    def _on_messages(
        self, coordinates: MessageCoordinates, _argument: str, client: Client
    ):
        if self.storage is None:
            logging.info("Cannot use Messages without storage")
            return

        rows = self.storage.messages_read(num_to_id(coordinates.from_id))
        if len(rows) == 0:
            client.send_response(message="📭", message_coordinates=coordinates)

        if not coordinates.is_dm:
            client.send_response(message="📬", message_coordinates=coordinates)

        new_coordinates = copy.deepcopy(coordinates)
        new_coordinates.is_dm = True
        new_coordinates.message_id = None

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
                current_message += f"\n{message}" if current_message else message
            else:
                concatenated_messages.append(current_message)
                current_message = message

        if current_message:
            concatenated_messages.append(current_message)

        for message in concatenated_messages:
            client.send_response(message=message, message_coordinates=new_coordinates)
