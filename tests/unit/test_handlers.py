# -*- coding: utf-8 -*-

import unittest
from unittest.mock import Mock, patch
import datetime
from tests.helpers import cases
from api import MethodRequest, online_score_handler, clients_interest_handler, ADMIN_LOGIN


class TestOnlineScoreHandler(unittest.TestCase):

    @patch('scoring.get_score', return_value=100500)
    @cases([
        {'phone': 71111111111, 'email': 'foo@bar.com'},
        {'gender': 1, 'birthday': datetime.datetime.today().strftime('%d.%m.%Y'), 'first_name': 'foo', 'last_name': 'bar'},
        {'gender': 0, 'birthday': datetime.datetime.today().strftime('%d.%m.%Y')},
        {'gender': 2, 'birthday': datetime.datetime.today().strftime('%d.%m.%Y')},
        {'first_name': 'foo', 'last_name': 'bar'},
        {'phone': 71111111111, 'email': 'foo@bar.com', 'gender': 1, 'birthday': '01.01.2000',
         'first_name': 'foo', 'last_name': 'bar'},
    ])
    def test_online_score_ok(self, mock_func, arguments):
        ctx = {}
        store = Mock()
        request_dict = {'account': '', 'login': 'login', 'token': '', 'method': 'foobar', 'arguments': arguments}
        request = MethodRequest(**request_dict)
        response = online_score_handler(request=request, ctx=ctx, store=store)
        self.assertIn('score', response.response)
        self.assertIn('has', ctx)
        self.assertEqual(sorted(ctx['has']), sorted(arguments.keys()))

    @cases([
        {'phone': 71111111111, 'email': 'foo@bar.com'}
    ])
    def test_online_score_admin_response(self, arguments):
        ctx = {}
        store = Mock()
        request_dict = {"account": "", "login": ADMIN_LOGIN, "token": "", "arguments": arguments, "method": "foobar"}
        request = MethodRequest(**request_dict)
        response = online_score_handler(request=request, ctx=ctx, store=store)
        self.assertEqual(response.response['score'], 42)


class TestClientsInterestHandler(unittest.TestCase):

    @patch('scoring.get_interests', return_value=['foo', 'bar'])
    @cases([
        {'client_ids': [1, 2, 3], 'date': datetime.datetime.today().strftime('%d.%m.%Y')},
        {'client_ids': [1], 'date': datetime.datetime.today().strftime('%d.%m.%Y')},
    ])
    def test_clients_interest_handler_ok(self, mock_func, arguments):
        ctx = {}
        store = Mock()
        request_dict = {'account': '', 'login': 'login', 'token': '', 'method': 'foobar', 'arguments': arguments}
        request = MethodRequest(**request_dict)
        response = clients_interest_handler(request=request, ctx=ctx, store=store)

        self.assertIn('nclients', ctx)
        self.assertEqual(ctx['nclients'], len(arguments['client_ids']))
        self.assertEqual(
            sorted(response.response.keys()),
            arguments['client_ids']
        )


if __name__ == '__main__':
    unittest.main()
