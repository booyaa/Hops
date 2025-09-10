"""
Command Line Interface for running 'Hops', a meshtastic bot
"""

import sys
import argparse
import logging
import time
from meshtastic.tcp_interface import TCPInterface
from meshtastic.serial_interface import SerialInterface
from .client import Client
from .hops import Hops
from .storage import Storage


def main():
    """
    main
    """
    parser = argparse.ArgumentParser(description="Run the hops bot")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    parser.add_argument(
        "--tcp", type=str, help="Specify the TCP hostname or IP address"
    )
    parser.add_argument(
        "--db",
        type=str,
        default="./db.sqlite",
        help="Specify the path to the database (default: ./db.sqlite)",
    )
    parser.add_argument(
        "--serial", action="store_true", help="Enable serial streaming mode"
    )
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)

    storage = None
    if args.db is not None:
        storage = Storage(args.db)

    interface = None
    if args.serial:
        interface = SerialInterface()
    elif args.tcp is not None:
        interface = TCPInterface(hostname=args.tcp)
    if interface is None:
        print("Error: One of --tcp or --serial must be defined", file=sys.stderr)
        sys.exit(1)

    hops = Hops(storage)

    _ = Client(interface, hops, storage)
    try:
        logging.info("Hops running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Bot stopped.")
