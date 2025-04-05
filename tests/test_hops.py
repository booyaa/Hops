"""
Test the Hops class
"""
import unittest
from unittest.mock import MagicMock
from hops.hops import Hops
from hops.client import Client

class TestHops(unittest.TestCase):
    """
    Test the Hops class
    """
    def setUp(self):
        self.hops = Hops()
        self.client = MagicMock(spec=Client)

    from_id = '1'
    to_id = '2'
    rx_id = '3'
    channel_index = 0

    def test_on_message_hello(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            from_id = self.from_id,
            channel_index = self.channel_index,
            rx_id = self.rx_id,
            message = '.hello',
            client = self.client,
        )
        self.client.send_text.assert_called_once_with('👋', channel_index = self.channel_index, destination_id=self.from_id)

    def test_on_message_hello_synonym(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            from_id = self.from_id,
            channel_index = self.channel_index,
            rx_id = self.rx_id,
            message = '.👋🏼',
            client = self.client,
        )
        self.client.send_text.assert_called_once_with('👋', channel_index = self.channel_index, destination_id=self.from_id)

    def test_on_message_no_prefix(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            from_id = self.from_id,
            channel_index = self.channel_index,
            rx_id = self.rx_id,
            message = 'hello',
            client = self.client,
        )
        self.client.send_text.assert_not_called()

    def test_on_message_unknown_command(self):
        """
        Ensure that nothing happens for unknown commands
        """
        self.hops.on_message(
            from_id = self.from_id,
            channel_index = self.channel_index,
            rx_id = self.rx_id,
            message = '.unknown',
            client = self.client,
        )
        self.client.send_text.assert_not_called()

    def test_on_message_non_command(self):
        """
        Ensure that nothing happens for unknown commands
        """
        self.hops.on_message(
            from_id = self.from_id,
            channel_index = self.channel_index,
            rx_id = self.rx_id,
            message = 'not a command',
            client = self.client,
        )
        self.client.send_text.assert_not_called()

if __name__ == '__main__':
    unittest.main()
