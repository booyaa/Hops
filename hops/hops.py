"""
Bot
"""
import logging
import argparse
from .client import Client

class Hops:
    """
    Handler for messages which will be parsed as commands with an attempt being made
    to execute the command if possible with replies going back to the `client`.
    """

    synonyms = {
        '👋🏼': 'hello',
    }

    def on_message(self, sender: str, to: str, rx_id: str, message: str, client: Client) -> None:
        """
        Handler for incoming messages
        """
        split = message.split(' ', 2)
        command = split[0]
        command = self.synonyms[command] if command in self.synonyms else command

        method_name = f'_on_{command.lower()}'
        if hasattr(self, method_name):

            method = getattr(self, method_name)
            if callable(method):
                arguments = split[1] if len(split) > 1 else None
                logging.debug('Received %s', command)
                method(sender, to, rx_id, arguments, client)

    def _on_hello(self, _sender: str, _to: str, _rx_id: str, _argument: str, client: Client) -> None:
        """
        Say hello
        """
        client.send_text('👋🏼')

    def _on_ping(self, _sender: str, _to: str, _rx_id: str, _argument: str, client: Client) -> None:
        """
        Respond to a ping
        """
        client.send_text('ack')

    def _on_weather(self, _sender: str, _to: str, _rx_id: str, _argument: str, _client: Client) -> None:
        """
        Get the weather
        """
        parser = argparse.ArgumentParser(description="Get the weather")
        _args = parser.parse_args()
