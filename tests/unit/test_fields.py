# -*- coding: utf-8 -*-

import unittest
import datetime
from tests.helpers import cases
from api import ValidationError, CharField, ArgumentsField, EmailField, PhoneField, DateField, \
    BirthDayField, NumericField, GenderField, ListField, ClientIDsField


class TestCharField(unittest.TestCase):

    def setUp(self):
        self.field = CharField()

    @cases([
        "",
        "foobar",
        str(100500),
        "foo" + "bar"
    ])
    def test_char_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        None,
        0,
        100500,
        [],
        {},
    ])
    def test_char_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


class TestArgumentField(unittest.TestCase):

    def setUp(self):
        self.field = ArgumentsField()

    @cases([
        {"foo": "bar", "foobar": 100500},
        dict(a=1, b=2),
        {},
    ])
    def test_argument_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        None,
        100500,
        "",
        []
    ])
    def test_argument_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


class TestEmailField(unittest.TestCase):

    def setUp(self):
        self.field = EmailField()

    @cases([
        'foo@bar.com'
    ])
    def test_email_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        None,
        "foobar",
        "foobar.com",
        "@",
        "foo@bar"
        "foo@bar."

    ])
    def test_email_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


class TestPhoneField(unittest.TestCase):
    def setUp(self):
        self.field = PhoneField()

    @cases([
        '71111111111',
        72222222222
    ])
    def test_phone_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        '',
        None,
        [],
        {},
        100500,
        7333333333,
        744444444444,
        '7a1111111111',
        '75555555555a',
        '+71112223344',
        '+7(111)222-33-44'

    ])
    def test_phone_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


class TestDateField(unittest.TestCase):
    def setUp(self):
        self.field = DateField()

    @cases([
        '01.01.2020',
        '1.1.2020',
        '13.01.2020'
    ])
    def test_date_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        '',
        None,
        {},
        [],
        '01.13.2020',
        '2020.01.01'
        '01-01-2020',
        '01/01/2020',
        12122020
    ])
    def test_date_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


class TestNumericField(unittest.TestCase):

    def setUp(self):
        self.field = NumericField()

    @cases([
        0,
        100500,
        int('100500')
    ])
    def test_numeric_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        None,
        '0',
        str(100500),
        4.2
    ])
    def test_numeric_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


class TestListField(unittest.TestCase):

    def setUp(self):
        self.field = ListField()

    @cases([
        [],
        [1, 2],
        ['a', 'b']
    ])
    def test_list_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        None,
        {},
        '',
        100500,
        'foobar'
    ])
    def test_list_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


class TestGenderField(unittest.TestCase):

    def setUp(self):
        self.field = GenderField()

    @cases([
        0,
        1,
        2,
    ])
    def test_gender_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        None,
        {},
        '',
        100500,
        'foobar',
        '0',
        '1',
        '2',
        3
    ])
    def test_gender_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


class TestClientIDsField(unittest.TestCase):

    def setUp(self):
        self.field = ClientIDsField()

    @cases([
        [0],
        [1],
        [1, 2, 3]
    ])
    def test_client_ids_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        None,
        {},
        '',
        100500,
        'foobar',
        ['0'],
        [1.0],
        ['1', '2'],
        ['a', 'b', 'c']
    ])
    def test_client_ids_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


class TestBirthDayField(unittest.TestCase):

    def setUp(self):
        self.field = BirthDayField()

    @cases([
        datetime.datetime.now().strftime('%d.%m.%Y'),
        (datetime.datetime.now() - datetime.timedelta(365 * 70)).strftime('%d.%m.%Y')
    ])
    def test_birthday_field_validate_ok(self, value):
        self.assertIsNone(self.field.validate(value))

    @cases([
        None,
        {},
        '',
        100500,
        'foobar',
        '01.13.2020',
        (datetime.datetime.now() - datetime.timedelta(365 * 71)).strftime('%d.%m.%Y'),
        (datetime.datetime.now() + datetime.timedelta(1)).strftime('%d.%m.%Y')
    ])
    def test_birthday_field_validate_error(self, value):
        with self.assertRaises(ValidationError):
            self.field.validate(value)


if __name__ == '__main__':
    unittest.main()
