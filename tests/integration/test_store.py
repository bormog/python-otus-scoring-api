# -*- coding: utf-8 -*-

import unittest
import logging
from unittest.mock import Mock
from store import RedisStore
from tests.helpers import cases
import time
import docker
from docker.errors import NotFound
from redis.exceptions import ConnectionError


class TestRedisStore(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.docker_client = docker.from_env()
        try:
            cls.container = cls.docker_client.containers.get('otus-test-redis')
            cls.container.start()
        except NotFound:
            cls.container = cls.docker_client.containers.run(
                'redis',
                name='otus-test-redis',
                ports={'6379/tcp': 6379},
                auto_remove=True,
                remove=True,
                detach=True
            )
        finally:
            cls.store = RedisStore()

    @classmethod
    def tearDownClass(cls):
        cls.container.stop()

    def setUp(self):
        logging.disable(logging.CRITICAL)
        self.store.connect()

    def tearDown(self):
        logging.disable(logging.NOTSET)
        self.store.client.flushdb()
        self.store.close()

    @cases([
        ['foo', b'bar'],
        ['foo', b'foobar'],
        ['foo', b'foo'],
    ])
    def test_cache_set_get(self, params):
        key, value = params
        self.store.cache_set(key, value, 5)
        cached_value = self.store.cache_get(key)
        self.assertEqual(value, cached_value)

    @cases([
        ['foo', b'bar'],
        ['foo', b'foobar'],
        ['foo', b'foo'],
    ])
    def test_cache_set_get_expire(self, params):
        key, value = params
        self.store.cache_set(key, value, 1)
        time.sleep(1.5)
        self.assertIsNone(self.store.cache_get(key))

    @cases([
        ['foo', [b'foo', b'bar']],
        ['bar', [b'foobar', b'barfoo']]
    ])
    def test_storage_set_get(self, params):
        key, values = params
        self.store.set(key, *values)
        stored_values = self.store.get(key)
        self.assertEqual(sorted(values), sorted(stored_values))

    @cases([
        'foo',
        'bar'
    ])
    def test_storage_get_not_exists(self, key):
        self.assertEqual(self.store.get(key), set())

    def test_storage_set_get_after_lost_connection(self):
        self.store.client = Mock(
            sadd=Mock(side_effect=ConnectionError),
            smembers=Mock(side_effect=ConnectionError),
            set=Mock(side_effect=ConnectionError),
            get=Mock(side_effect=ConnectionError),
        )

        with self.assertRaises(ConnectionError):
            self.store.set('foo', 'foobar')

        with self.assertRaises(ConnectionError):
            self.store.get('foo')
