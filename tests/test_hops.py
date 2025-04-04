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

    def test_on_message_hello(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message('sender', 'receiver', 'rxid', 'hello', self.client)
        self.client.send_text.assert_called_once_with('👋🏼')

    def test_on_message_hello_synonym(self):
        """
        Ensure that the hello message is properly responded to
        """
        self.hops.on_message('sender', 'receiver', 'rxid', '👋🏼', self.client)
        self.client.send_text.assert_called_once_with('👋🏼')

    def test_on_message_unknown_command(self):
        """
        Ensure that nothing happens for unknown commands
        """
        self.hops.on_message('unknown', 'sender', 'receiver', 'rxid', self.client)
        self.client.send_text.assert_not_called()

if __name__ == '__main__':
    unittest.main()
