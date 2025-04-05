"""
Test the Hops class
"""
import unittest
from unittest.mock import MagicMock
from hops.hops import Hops
from hops.client import Client
from hops.storage import Storage
from hops.message_coordinates import MessageCoordinates

class TestHops(unittest.TestCase):
    """
    Test the Hops class
    """
    def setUp(self):
        self.storage = MagicMock(spec=Storage)
        self.hops = Hops(storage=self.storage)
        self.client = MagicMock(spec=Client)
        self.message_coordinates = MessageCoordinates(
            from_id = '1',
            from_node = None,
            to_id = '2',
            to_node = None,
            message_id = '3',
            channel_index = 0,
            is_dm = False,
        )

    def test_on_bbs_insert(self):
        """
        Test the insertion of a BBS message and verify the correct storage call.
        """
        self.hops.on_message(
            self.message_coordinates,
            message = '.bbs add Hello',
            client = self.client,
        )
        self.storage.bbs_insert.assert_called_once_with(
            from_id = self.message_coordinates.from_id,
            from_short_name = None,
            from_long_name = None,
            channel_index = self.message_coordinates.channel_index,
            message = 'Hello',
        )

    def test_on_bbs_list(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            self.message_coordinates,
            message = '.bbs',
            client = self.client,
        )
        self.storage.bbs_read.assert_called_once_with(
            channel_index = self.message_coordinates.channel_index,
        )

    def test_on_bbs_help(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            self.message_coordinates,
            message = '.bbs help',
            client = self.client,
        )
        self.storage.bbs_read.assert_not_called()
        self.client.send_response.assert_called_once()

if __name__ == '__main__':
    unittest.main()
