# -*- coding: utf-8 -*-

import unittest
from store import RedisStore
from tests.helpers import cases
from scoring import get_interests
import docker
from docker.errors import NotFound
import time


class TestGetInterests(unittest.TestCase):
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
        ['foo', ["cars", "pets", "travel", "hi-tech", "sport"]],
    ])
    def test_get_interests(self, params):
        cid, values = params
        if len(values):
            key = 'i#%s' % cid
            self.store.set(key, *values)
        result = get_interests(self.store, cid)

        self.assertEqual(
            sorted(values),
            sorted(result)
        )
