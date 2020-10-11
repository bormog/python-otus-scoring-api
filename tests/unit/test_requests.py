# -*- coding: utf-8 -*-

import unittest
import datetime
from tests.helpers import cases
from api import ValidationError, BaseField, BaseRequest, ClientsInterestsRequest, \
    OnlineScoreRequest, MethodRequest
from api import ADMIN_LOGIN


def build_request_object(obj_name, field_name, required, nullable):
    def _validate(self, value):
        return

    field_cls = type('%sField' % obj_name, (BaseField, ), dict(validate=_validate))
    fields = {
        field_name: field_cls(required=required, nullable=nullable)
    }
    return type('%sRequest' % obj_name, (BaseRequest,), fields)


class TestRequestRequiredNullable(unittest.TestCase):

    def setUp(self):
        self.request_cls = build_request_object('FooBar', 'foobar', required=True, nullable=True)

    def tearDown(self):
        self.request = None

    @cases([
        {'foobar': ''},
        {'foobar': 0},
        {'foobar': {}},
        {'foobar': []},
    ])
    def test_request_required_nullable_validate_ok(self, values):
        request = self.request_cls(**values)
        self.assertIsNone(request.validate())

    @cases([
        {'foobar': None},
        {}
    ])
    def test_request_required_nullable_validate_error(self, values):
        request = self.request_cls(**values)
        with self.assertRaises(ValidationError):
            request.validate()


class TestRequestRequiredNotNullable(unittest.TestCase):

    def setUp(self):
        self.request_cls = build_request_object('FooBar', 'foobar', required=True, nullable=False)

    def tearDown(self):
        self.request = None

    @cases([
        {'foobar': 'foobar'},
    ])
    def test_request_required_not_nullable_validate_ok(self, values):
        request = self.request_cls(**values)
        self.assertIsNone(request.validate())

    @cases([
        {'foobar': 0},
        {'foobar': ''},
        {'foobar': []},
        {'foobar': {}},
        {'foobar': None},
        {}
    ])
    def test_request_required_not_nullable_validate_error(self, values):
        request = self.request_cls(**values)
        with self.assertRaises(ValidationError):
            request.validate()


class TestRequestNotRequiredNullable(unittest.TestCase):

    def setUp(self):
        self.request_cls = build_request_object('FooBar', 'foobar', required=False, nullable=True)

    def tearDown(self):
        self.request = None

    @cases([
        {},
        {'foobar': None},
        {'foobar': 0},
        {'foobar': ''},
        {'foobar': []},
        {'foobar': {}}
    ])
    def test_request_not_required_nullable_validate_ok(self, values):
        request = self.request_cls(**values)
        self.assertIsNone(request.validate())


class TestRequestNotRequiredNotNullable(unittest.TestCase):

    def setUp(self):
        self.request_cls = build_request_object('FooBar', 'foobar', required=False, nullable=False)

    def tearDown(self):
        self.request = None

    @cases([
        {},
        {'foobar': None},
        {'foobar': 'foobar'}
    ])
    def test_request_not_required_not_nullable_validate_ok(self, values):
        request = self.request_cls(**values)
        self.assertIsNone(request.validate())

    @cases([
        {'foobar': 0},
        {'foobar': ''},
        {'foobar': []},
        {'foobar': {}}
    ])
    def test_request_not_required_not_nullable_validate_error(self, values):
        request = self.request_cls(**values)
        with self.assertRaises(ValidationError):
            request.validate()


class TestClientsInterestsRequest(unittest.TestCase):

    def setUp(self):
        self.request_cls = ClientsInterestsRequest

    def tearDown(self):
        self.request_cls = None

    @cases([
        {"client_ids": [1, 2, 3], "date": datetime.datetime.today().strftime("%d.%m.%Y")},
        {"client_ids": [1, 2], "date": "19.07.2017"},
        {"client_ids": [0]},
    ])
    def test_clients_interests_request_validate_ok(self, values):
        request = self.request_cls(**values)
        self.assertIsNone(request.validate())

    @cases([
        {},
        {"date": "20.07.2017"},
        {"client_ids": [], "date": "20.07.2017"},
        {"client_ids": {1: 2}, "date": "20.07.2017"},
        {"client_ids": ["1", "2"], "date": "20.07.2017"},
        {"client_ids": [1, 2], "date": "XXX"},
    ])
    def test_clients_interests_request_validate_error(self, values):
        request = self.request_cls(**values)
        with self.assertRaises(ValidationError):
            request.validate()


class TestOnlineScoreRequest(unittest.TestCase):

    def setUp(self):
        self.request_cls = OnlineScoreRequest

    def tearDown(self):
        self.request_cls = None

    @cases([
        {"phone": "79175002040", "email": "stupnikov@otus.ru"},
        {"phone": 79175002040, "email": "stupnikov@otus.ru"},
        {"gender": 1, "birthday": "01.01.2000", "first_name": "a", "last_name": "b"},
        {"gender": 0, "birthday": "01.01.2000"},
        {"gender": 2, "birthday": "01.01.2000"},
        {"first_name": "a", "last_name": "b"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "a", "last_name": "b"},
    ])
    def test_online_score_request_validate_ok(self, values):
        request = self.request_cls(**values)
        self.assertIsNone(request.validate())

    @cases([
        {},
        {"phone": "79175002040"},
        {"phone": "89175002040", "email": "stupnikov@otus.ru"},
        {"phone": "79175002040", "email": "stupnikovotus.ru"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": -1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": "1"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.1890"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "XXX"},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000", "first_name": 1},
        {"phone": "79175002040", "email": "stupnikov@otus.ru", "gender": 1, "birthday": "01.01.2000",
         "first_name": "s", "last_name": 2},
        {"phone": "79175002040", "birthday": "01.01.2000", "first_name": "s"},
        {"email": "stupnikov@otus.ru", "gender": 1, "last_name": 2},
    ])
    def test_online_score_request_validate_error(self, values):
        request = self.request_cls(**values)
        with self.assertRaises(ValidationError):
            request.validate()


class TestMethodRequest(unittest.TestCase):

    def setUp(self):
        self.request_cls = MethodRequest

    def tearDown(self):
        self.request_cls = None

    @cases([
        {"account": "account", "login": "login", "token": "token", "arguments": {"foo": "bar"}, "method": "foobar"},
        {"login": "login", "token": "token", "arguments": {"foo": "bar"}, "method": "foobar"},
        {"account": "", "login": "", "token": "", "arguments": {}, "method": "foobar"},
    ])
    def test_method_request_validate_ok(self, values):
        request = self.request_cls(**values)
        self.assertIsNone(request.validate())

    @cases([
        {"account": "horns&hoofs", "login": "h&f", "method": "online_score"},
        {"account": "horns&hoofs", "login": "h&f", "arguments": {}},
        {"account": "horns&hoofs", "method": "online_score", "arguments": {}},
    ])
    def test_method_request_validate_error(self, values):
        request = self.request_cls(**values)
        with self.assertRaises(ValidationError):
            request.validate()

    @cases([
        {"account": "", "login": ADMIN_LOGIN, "token": "", "arguments": {}, "method": "foobar"},
    ])
    def test_method_request_is_admin(self, values):
        request = self.request_cls(**values)
        self.assertTrue(request.is_admin)

    @cases([
        {"account": "", "login": "", "token": "", "arguments": {}, "method": "foobar"},
        {"account": "", "login": "foobar", "token": "", "arguments": {}, "method": "foobar"},
    ])
    def test_method_request_is_not_admin(self, values):
        request = self.request_cls(**values)
        self.assertFalse(request.is_admin)


if __name__ == '__main__':
    unittest.main()


