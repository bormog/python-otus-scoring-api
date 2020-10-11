# -*- coding: utf-8 -*-
import redis
import time
import logging

REDIS_RETRY_COUNT = 3
REDIS_WAIT_TIME = 0.2


def retry(raise_on_failure=True):

    def retry_on_failure(method):

        def wrapper(*args, **kwargs):
            last_exception = None
            for i in range(REDIS_RETRY_COUNT):
                try:
                    return method(*args, **kwargs)
                except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                    last_exception = e
                    time.sleep(REDIS_WAIT_TIME)

            if last_exception is not None:
                msg = 'Method %s was failed after %d attempts' % (method, REDIS_RETRY_COUNT)
                logging.exception(msg, exc_info=last_exception)

            if raise_on_failure:
                raise last_exception

        return wrapper
    return retry_on_failure


class RedisStore(object):

    client = None
    params = {}

    def __init__(self, **kwargs):
        self.params = kwargs

    def connect(self):
        try:
            self.client = redis.Redis(**self.params)
            self.client.ping()
        except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError):
            raise

    @retry(raise_on_failure=True)
    def set(self, key, *values):
        return self.client.sadd(key, *values)

    @retry(raise_on_failure=True)
    def get(self, key):
        return self.client.smembers(key)

    @retry(raise_on_failure=False)
    def cache_set(self, key, value, expire):
        return self.client.set(key, value, ex=expire)

    @retry(raise_on_failure=False)
    def cache_get(self, key):
        return self.client.get(key)


