# -*- coding: utf-8 -*-

import unittest
from tests.helpers import cases
from api import check_auth, SALT, MethodRequest
import hashlib


class TestCheckAuth(unittest.TestCase):

    @cases([
        {"account": "", "login": "", "token": hashlib.sha512(SALT.encode('utf-8')).hexdigest()},
        {"account": "foo", "login": "bar", "token": hashlib.sha512(("foobar" + SALT).encode('utf-8')).hexdigest()}
    ])
    def test_check_auth_is_true(self, values):
        request = MethodRequest(**values)
        self.assertTrue(check_auth(request))

    @cases([
        {"account": "", "login": "", "token": ""},
        {"account": "foo", "login": "bar", "token": hashlib.sha512(SALT.encode('utf-8')).hexdigest()}
    ])
    def test_check_auth_is_false(self, values):
        request = MethodRequest(**values)
        self.assertFalse(check_auth(request))