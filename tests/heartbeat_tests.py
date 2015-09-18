__author__ = 'eandersson'

import time
import logging

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from amqpstorm.heartbeat import Heartbeat
from amqpstorm.exception import AMQPConnectionError

logging.basicConfig(level=logging.DEBUG)


class HeartbeatTests(unittest.TestCase):
    def test_heartbeat_start(self):
        heartbeat = Heartbeat(1)
        heartbeat.start([])
        self.assertIsNotNone(heartbeat._timer)
        heartbeat.stop()

    def test_heartbeat_stop(self):
        heartbeat = Heartbeat(1)
        heartbeat.start([])
        heartbeat.stop()
        self.assertIsNone(heartbeat._timer)

    def test_register_beat(self):
        heartbeat = Heartbeat(1)
        heartbeat.start([])
        self.assertEqual(heartbeat._beats_since_check, 0)
        heartbeat.register_beat()
        self.assertEqual(heartbeat._beats_since_check, 1)

    def test_register_heartbeat(self):
        heartbeat = Heartbeat(1)
        heartbeat.start([])
        last_heartbeat = heartbeat._last_heartbeat
        time.sleep(0.01)
        heartbeat.register_heartbeat()
        self.assertNotEqual(heartbeat._last_heartbeat, last_heartbeat)

    def test_basic_raise_on_missed_heartbeats(self):
        exceptions = []
        heartbeat = Heartbeat(0.5)
        heartbeat.start(exceptions)
        time.sleep(3)
        self.assertGreater(len(exceptions), 0)

    def test_basic_raise_when_check_for_life_when_exceptions_not_set(self):
        heartbeat = Heartbeat(0.5)
        heartbeat._beats_since_check = 0
        heartbeat._last_heartbeat = time.time() - 100

        # Normally the exception should be passed down to the list of
        # exceptions in the connection, but if that list for some obscure
        # reason is None, we should raise directly in _check_for_life_signs.
        self.assertRaises(AMQPConnectionError, heartbeat._check_for_life_signs)