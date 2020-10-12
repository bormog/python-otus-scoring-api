# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock, patch
from store import RedisStore
from redis.exceptions import TimeoutError, ConnectionError
import logging


class TestStoreConnection(unittest.TestCase):

    @classmethod
    @patch('redis.Redis')
    def setUpClass(cls, mock_func):
        cls.storage = RedisStore()
        kwargs = {
            'get.side_effect': ConnectionError,
            'smembers.side_effect': ConnectionError,
            'set.side_effect': ConnectionError,

        }
        cls.storage.client = Mock(**kwargs)

    def setUp(self):
        logging.disable(logging.CRITICAL)

    def tearDown(self):
        logging.disable(logging.NOTSET)

    @patch('store.REDIS_RETRY_DELAY', 0)
    @patch('store.REDIS_RETRY_MAX_ATTEMPTS', 1)
    def test_store_cache_set_no_failure(self):
        try:
            self.storage.cache_set('foo', 'bar', 1)
        except (TimeoutError, ConnectionError):
            self.fail('Method cache_set raises exception.')

    @patch('store.REDIS_RETRY_DELAY', 0)
    @patch('store.REDIS_RETRY_MAX_ATTEMPTS', 1)
    def test_store_cache_get_no_failure(self):
        try:
            self.storage.cache_get('foo')
        except (TimeoutError, ConnectionError):
            self.fail('Method cache_get raises exception.')

    @patch('store.REDIS_RETRY_DELAY', 0)
    @patch('store.REDIS_RETRY_MAX_ATTEMPTS', 5)
    def test_store_retry_count_ok(self):
        with self.assertRaises(ConnectionError):
            self.storage.get('foo')
        self.assertEqual(5, self.storage.client.smembers.call_count)


if __name__ == '__main__':
    unittest.main()


