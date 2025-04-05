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
            from_id="1",
            from_node=None,
            to_id="2",
            to_node=None,
            message_id="3",
            channel_index=0,
            is_dm=False,
        )

    def test_on_message_hello(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            self.message_coordinates,
            message=".hello",
            client=self.client,
        )
        self.client.send_response.assert_called_once_with(
            message="👋", message_coordinates=self.message_coordinates
        )

    def test_on_message_hello_synonym(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            self.message_coordinates,
            message=".👋🏼",
            client=self.client,
        )
        self.client.send_response.assert_called_once_with(
            message="👋", message_coordinates=self.message_coordinates
        )

    def test_on_message_no_prefix(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message(
            self.message_coordinates,
            message="hello",
            client=self.client,
        )
        self.client.send_response.assert_not_called()

    def test_on_message_unknown_command(self):
        """
        Ensure that nothing happens for unknown commands
        """
        self.hops.on_message(
            self.message_coordinates,
            message=".unknown",
            client=self.client,
        )
        self.client.send_response.assert_not_called()

    def test_on_message_non_command(self):
        """
        Ensure that nothing happens for unknown commands
        """
        self.hops.on_message(
            self.message_coordinates,
            message="not a command",
            client=self.client,
        )
        self.client.send_response.assert_not_called()


if __name__ == "__main__":
    unittest.main()
