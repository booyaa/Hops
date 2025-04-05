"""
Bot
"""
import logging
# import argparse
from typing import Optional
from .client import Client

class Hops:
    """
    Handler for messages which will be parsed as commands with an attempt being made
    to execute the command if possible with replies going back to the `client`.
    """

    prefix = '.'

    synonyms = {
        '👋': 'hello',
        '👋🏻': 'hello',
        '👋🏼': 'hello',
        '👋🏽': 'hello',
        '👋🏾': 'hello',
        '👋🏿': 'hello',
        'info': 'help',
        '?': 'help',
        '!': 'help',
        '🤨': 'help',
    }

    def on_message(
        self,
        from_id: Optional[str],
        channel_index: Optional[int],
        rx_id: str,
        message: str,
        client: Client
    ) -> None:
        """
        Handler for incoming messages
        """
        split = message.split(' ', 2)

        command = split[0]

        # Require that the command be prefixed with by '.'
        if not command.startswith(self.prefix):
            return
        command = command[1:]

        # Map synonyms to canonical names
        command = self.synonyms[command] if command in self.synonyms else command

        method_name = f'_on_{command.lower()}'
        if hasattr(self, method_name):
            method = getattr(self, method_name)
            if callable(method):
                arguments = split[1] if len(split) > 1 else None
                logging.debug('Received %s', command)
                method(from_id, channel_index, rx_id, arguments, client)

    def _on_hello(
        self,
        from_id: Optional[str],
        channel_index: Optional[int],
        _rx_id: str,
        _argument: str,
        client: Client
    ) -> None:
        """
        Say hello
        """
        client.send_text(
            '👋',
            channel_index = channel_index,
            destination_id = from_id
        )

    def _on_ping(
        self,
        from_id: Optional[str],
        channel_index: Optional[int],
        _rx_id: str,
        _argument: str,
        client: Client
    ) -> None:
        """
        Respond to a ping
        """
        client.send_text(
            'ack',
            channel_index = channel_index,
            destination_id = from_id,
        )

    def _on_help(
        self,
        from_id: Optional[str],
        channel_index: Optional[int],
        _rx_id: str,
        _argument: str,
        client: Client
    ) -> None:
        """
        Provide help info
        """
        client.send_text(
            'http://w2asm.com/hops',
            channel_index = channel_index,
            destination_id = from_id
        )

    # def _on_weather(
    #     self,
    #     _from_id: Optional[str],
    #     _channel_index: Optional[int],
    #     _rx_id: str,
    #     _argument: str,
    #     _client: Client
    # ) -> None:
    #     """
    #     Get the weather
    #     """
    #     parser = argparse.ArgumentParser(description="Get the weather")
    #     _args = parser.parse_args()
