# -*- coding: utf-8 -*-

import unittest
from store import RedisStore
from tests.helpers import cases
import time
import docker
from docker.errors import NotFound


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
            cls.store.connect()

    @classmethod
    def tearDownClass(cls):
        cls.store.close()
        cls.container.stop()

    def setUp(self):
        pass

    def tearDown(self):
        self.store.client.flushdb()

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
