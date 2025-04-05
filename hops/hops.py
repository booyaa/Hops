"""
Bot
"""
import logging
import argparse
from typing import Optional
from .client import Client
from .storage import Storage

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

    def __init__(self, storage: Optional[Storage] = None):
        """
        Initialize the Hops instance with optional storage.
        """
        self.storage = storage

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

        if self.storage is not None:
            self.storage.log_received(
                from_id, channel_index, message
            )
        
        split = message.split(' ', 1)

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
    
    def _on_bbs(
        self,
        from_id: Optional[str],
        channel_index: Optional[int],
        _rx_id: str,
        argument: str,
        client: Client
    ):
        parser = argparse.ArgumentParser(description="Bulletin Board System")
        parser.add_argument('command', choices=['help', 'add'], nargs='?', default=None)
        parser.add_argument('message', nargs=argparse.REMAINDER)
        args = parser.parse_args(argument.split() if argument else [])
        
        if args.command == 'help':
            client.send_text(
                'http://w2asm.com/hops/bbs/',
                channel_index=channel_index,
                destination_id=from_id
            )
            return

        if self.storage is None:
            logging.info('Cannot use BBS without storage')
            return
        
        if args.command == 'add':
            message = ' '.join(args.message if args.message is not None else [])
            self.storage.bbs_insert(
                from_id = from_id,
                from_short_name = None,
                from_long_name = None,
                channel_index = channel_index,
                message = message
            )
            return

        rows = self.storage.bbs_read(
                channel_index = channel_index,
            )

        for row in rows[0:5]:
            from_id = row['from_short_name'] if row['from_short_name'] is not None else row['from_id']
            message = f"{from_id}: {row['message']}"
            client.send_text(
                message,
                channel_index = channel_index,
                destination_id =  from_id,
            )
