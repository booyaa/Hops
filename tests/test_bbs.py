"""
Test the Hops class
"""
import unittest
from unittest.mock import MagicMock
from hops.hops import Hops
from hops.client import Client
from hops.storage import Storage

class TestHops(unittest.TestCase):
    """
    Test the Hops class
    """
    def setUp(self):
        self.storage = MagicMock(spec=Storage)
        self.hops = Hops(storage=self.storage)
        self.client = MagicMock(spec=Client)

    from_id = '1'
    to_id = '2'
    rx_id = '3'
    channel_index = 0

    def test_on_bbs_insert(self):
        """
        """
        self.hops.on_message(
            from_id = self.from_id,
            channel_index = self.channel_index,
            rx_id = self.rx_id,
            message = '.bbs add Hello',
            client = self.client,
        )
        self.storage.bbs_insert.assert_called_once_with(
            from_id = self.from_id,
            from_short_name = None,
            from_long_name = None,
            channel_index = self.channel_index,
            message = 'Hello',
        )

    def test_on_bbs_list(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            from_id = self.from_id,
            channel_index = self.channel_index,
            rx_id = self.rx_id,
            message = '.bbs',
            client = self.client,
        )
        self.storage.bbs_read.assert_called_once_with(
            channel_index = self.channel_index,
        )

    def test_on_bbs_help(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            from_id = self.from_id,
            channel_index = self.channel_index,
            rx_id = self.rx_id,
            message = '.bbs help',
            client = self.client,
        )
        self.storage.bbs_read.assert_not_called()
        self.client.send_text.assert_called_once()

if __name__ == '__main__':
    unittest.main()
