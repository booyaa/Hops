"""
Command Line Interface for running 'Hops', a meshtastic bot
"""
import argparse
import logging
import time
from meshtastic.tcp_interface import TCPInterface
from .client import Client
from .hops import Hops
from .storage import Storage

def main():
    """
    main
    """
    parser = argparse.ArgumentParser(description="Run the hops bot")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    if args.verbose:
        logging.basicConfig(level=logging.DEBUG)

    storage = Storage('./db.sqlite')
    interface = TCPInterface(hostname="192.168.1.66")
    hops = Hops(storage)

    _ = Client(interface, hops)
    try:
        logging.info("Hops running. Press Ctrl+C to stop.")
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Bot stopped.")
