#!/usr/bin/env python
# -*- coding: utf-8 -*-

import abc
import json
import datetime
import logging
import hashlib
import uuid
from optparse import OptionParser
from http.server import HTTPServer, BaseHTTPRequestHandler
from weakref import WeakKeyDictionary
import scoring
import re
from collections import namedtuple
from store import RedisStore

SALT = "Otus"
ADMIN_LOGIN = "admin"
ADMIN_SALT = "42"
OK = 200
BAD_REQUEST = 400
FORBIDDEN = 403
NOT_FOUND = 404
INVALID_REQUEST = 422
INTERNAL_ERROR = 500
ERRORS = {
    BAD_REQUEST: "Bad Request",
    FORBIDDEN: "Forbidden",
    NOT_FOUND: "Not Found",
    INVALID_REQUEST: "Invalid Request",
    INTERNAL_ERROR: "Internal Server Error",
}
UNKNOWN = 0
MALE = 1
FEMALE = 2
GENDERS = {
    UNKNOWN: "unknown",
    MALE: "male",
    FEMALE: "female",
}

Response = namedtuple('Response', ['response', 'code'])


class ValidationError(ValueError):
    pass


class BaseField(metaclass=abc.ABCMeta):

    def __init__(self, required=False, nullable=False):
        self.required = required
        self.nullable = nullable
        self.data = WeakKeyDictionary()

    def __set_name__(self, owner, name):
        self.name = name

    def __set__(self, instance, value):
        self.data[instance] = value

    def __get__(self, instance, owner):
        return self.data.get(instance)

    @abc.abstractmethod
    def validate(self, value):
        pass


class CharField(BaseField):
    def validate(self, value):
        if not isinstance(value, str):
            raise ValidationError('%s is not a string' % value)


class ArgumentsField(BaseField):
    def validate(self, value):
        if not isinstance(value, dict):
            raise ValidationError('%s is not a dict' % value)


class EmailField(CharField):
    def validate(self, value):
        super(EmailField, self).validate(value)
        if not re.match(r'^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$', value):
            raise ValidationError('email must contain @')


class PhoneField(BaseField):
    def validate(self, value):
        if not re.match(r'^7[0-9]{10}$', str(value)):
            raise ValidationError('phone must be 11 symbols length and start with 7')


class DateField(CharField):
    def validate(self, value):
        super(DateField, self).validate(value)
        try:
            datetime.datetime.strptime(value, '%d.%m.%Y')
        except (ValueError, TypeError):
            raise ValidationError("date format must me DD.MM.YYYY")


class BirthDayField(DateField):
    MAX_AGE = 70

    def validate(self, value):
        super(BirthDayField, self).validate(value)
        datetime_obj = datetime.datetime.strptime(value, '%d.%m.%Y')
        if datetime.datetime.now().year - datetime_obj.year > self.MAX_AGE:
            raise ValidationError("too old, max 70 years")
        if datetime_obj > datetime.datetime.now():
            raise ValidationError('date cant be in future')


class NumericField(BaseField):
    def validate(self, value):
        if not isinstance(value, int):
            raise ValidationError('must be int')


class GenderField(NumericField):
    def validate(self, value):
        super(GenderField, self).validate(value)
        if value not in GENDERS.keys():
            raise ValidationError('gender must be 0, 1 or 2')


class ListField(BaseField):
    def validate(self, value):
        if not isinstance(value, list):
            raise ValidationError('must be a list')


class ClientIDsField(ListField):
    def validate(self, value):
        super(ClientIDsField, self).validate(value)
        for v in value:
            if not isinstance(v, int):
                raise ValidationError('must be a list of int')


class BaseRequest(object):

    def __new__(cls, *args, **kwargs):
        cls.fields = [k for k, v in cls.__dict__.items() if isinstance(v, BaseField)]
        return super(BaseRequest, cls).__new__(cls)

    def __init__(self, **kwargs):
        for field in self.fields:
            setattr(self, field, kwargs.get(field))

    def validate(self):
        errors = []
        for name in self.fields:
            field = self.__class__.__dict__.get(name)
            value = getattr(self, name)

            """
            A: required = True <=> value != None 
            B: nullable = False <=> value != "",0, (),[], {}
                
            required = True and nullable = True
                A     
            required = True and nullable = False
                A + B
            required = False and nullable = True
                pass
            required = False and nullable = False
                B
                
            validate:
                if value != None and value not empty        
            """
            if field.required:
                if value is None:
                    errors.append('Field %s has error: this field is required' % name)
                    continue
                if not field.nullable:
                    if value in ("", 0, (), [], {}):
                        errors.append('Field %s has error: this field can not be empty' % name)
                        continue
            elif not field.nullable:
                if value in ("", 0, (), [], {}):
                    errors.append('Field %s has error: this field can not be empty' % name)
                    continue

            if value not in (None, "", 0, (), [], {}):
                try:
                    field.validate(value)
                except ValidationError as e:
                    errors.append('Field %s has error:  %s' % (name, str(e)))

        if len(errors):
            raise ValidationError(', '.join(errors))


class ClientsInterestsRequest(BaseRequest):
    client_ids = ClientIDsField(required=True)
    date = DateField(required=False, nullable=True)


class OnlineScoreRequest(BaseRequest):
    first_name = CharField(required=False, nullable=True)
    last_name = CharField(required=False, nullable=True)
    email = EmailField(required=False, nullable=True)
    phone = PhoneField(required=False, nullable=True)
    birthday = BirthDayField(required=False, nullable=True)
    gender = GenderField(required=False, nullable=True)

    def validate(self):
        super(OnlineScoreRequest, self).validate()
        if not any([
            self.phone and self.email,
            self.first_name and self.last_name,
            self.gender in GENDERS.keys() and self.birthday
        ]):
            raise ValidationError('phone-email or first_name-last_name or gender-birthday must be not empty')


class MethodRequest(BaseRequest):
    account = CharField(required=False, nullable=True)
    login = CharField(required=True, nullable=True)
    token = CharField(required=True, nullable=True)
    arguments = ArgumentsField(required=True, nullable=True)
    method = CharField(required=True, nullable=False)

    @property
    def is_admin(self):
        return self.login == ADMIN_LOGIN


def check_auth(request):
    if request.is_admin:
        digest = hashlib.sha512((datetime.datetime.now().strftime("%Y%m%d%H") + ADMIN_SALT).encode('utf-8')).hexdigest()
    else:
        digest = hashlib.sha512((request.account + request.login + SALT).encode('utf-8')).hexdigest()
    if digest == request.token:
        return True
    return False


def clients_interest_handler(request, ctx, store):
    model = ClientsInterestsRequest(**request.arguments)
    model.validate()

    ctx['nclients'] = len(model.client_ids)

    response = {x: scoring.get_interests(store, x) for x in model.client_ids}
    return Response(response, OK)


def online_score_handler(request, ctx, store):
    model = OnlineScoreRequest(**request.arguments)
    model.validate()

    ctx['has'] = [name for name in model.fields if getattr(model, name) is not None]

    if request.is_admin:
        response, code = dict(score=42), OK
    else:
        score = scoring.get_score(store=store,
                                  phone=model.phone,
                                  email=model.email,
                                  birthday=model.birthday,
                                  gender=model.gender,
                                  first_name=model.first_name,
                                  last_name=model.last_name)
        response, code = dict(score=score), OK
    return Response(response, code)


def get_handler(method):
    handlers = {
        'online_score': online_score_handler,
        'clients_interests': clients_interest_handler
    }
    return handlers.get(method, None)


def method_handler(request, ctx, store):
    request_dict = request.get('body')
    if not isinstance(request_dict, dict):
        return Response(response='Request body must be a valid dictionary', code=INVALID_REQUEST)

    try:
        method_request = MethodRequest(**request_dict)
        method_request.validate()
    except ValidationError as e:
        logging.exception(e)
        return Response(response=str(e), code=INVALID_REQUEST)

    if not check_auth(method_request):
        return Response(response=None, code=FORBIDDEN)

    handler = get_handler(method_request.method)
    if not handler:
        return Response(response='Unknown method %s' % str(method_request.method), code=INVALID_REQUEST)

    try:
        return handler(request=method_request, ctx=ctx, store=store)
    except ValidationError as e:
        logging.exception(e)
        return Response(response=str(e), code=INVALID_REQUEST)


class MainHTTPHandler(BaseHTTPRequestHandler):
    router = {
        "method": method_handler
    }
    store = RedisStore(socket_connect_timeout=30)

    def get_request_id(self, headers):
        return headers.get('HTTP_X_REQUEST_ID', uuid.uuid4().hex)

    def do_POST(self):
        response, code = {}, OK
        context = {"request_id": self.get_request_id(self.headers)}
        request = None
        try:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            request = json.loads(data_string)
        except:
            code = BAD_REQUEST

        if request:
            path = self.path.strip("/")
            logging.info("%s: %s %s" % (self.path, data_string, context["request_id"]))
            if path in self.router:
                try:
                    response, code = self.router[path]({"body": request, "headers": self.headers}, context, self.store)
                except Exception as e:
                    logging.exception("Unexpected error: %s" % e)
                    code = INTERNAL_ERROR
            else:
                code = NOT_FOUND

        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        if code not in ERRORS:
            r = {"response": response, "code": code}
        else:
            r = {"error": response or ERRORS.get(code, "Unknown Error"), "code": code}
        context.update(r)
        logging.info(context)
        self.wfile.write(json.dumps(r).encode('utf_8'))
        return


if __name__ == "__main__":
    op = OptionParser()
    op.add_option("-p", "--port", action="store", type=int, default=8080)
    op.add_option("-l", "--log", action="store", default=None)
    (opts, args) = op.parse_args()
    logging.basicConfig(filename=opts.log, level=logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s', datefmt='%Y.%m.%d %H:%M:%S')
    MainHTTPHandler.store.connect()
    server = HTTPServer(("localhost", opts.port), MainHTTPHandler)
    logging.info("Starting server at %s" % opts.port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    server.server_close()
