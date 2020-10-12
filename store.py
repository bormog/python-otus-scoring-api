# -*- coding: utf-8 -*-
import redis
import time
import logging

REDIS_RETRY_MAX_ATTEMPTS = 3
REDIS_RETRY_DELAY = 0.1


def retry(raise_on_failure=True):

    def retry_on_failure(method):

        def wrapper(*args, **kwargs):
            last_exception = None
            delay = REDIS_RETRY_DELAY
            for i in range(REDIS_RETRY_MAX_ATTEMPTS):
                try:
                    return method(*args, **kwargs)
                except (redis.exceptions.ConnectionError, redis.exceptions.TimeoutError) as e:
                    last_exception = e
                    time.sleep(delay)
                    delay *= 2

            if last_exception is not None:
                msg = 'Method %s was failed after %d attempts' % (method, REDIS_RETRY_MAX_ATTEMPTS)
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

    @retry(raise_on_failure=True)
    def connect(self):
        self.client = redis.Redis(**self.params)
        self.client.ping()

    def close(self):
        self.client.close()

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


