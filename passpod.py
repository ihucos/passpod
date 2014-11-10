# The MIT License (MIT)
#
# Copyright (c) 2014 Irae Hueck Costa
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

'''
Passpod is a library to securely save user passwords.
See READEM.md for more information.

We can open any SQL database with a sqlalchmey database url.
>>> passwords = open('sqlite:///:memory:')

A dict-like interface is returned which can be used to save passwords.
>>> passwords['user1'] = 'pass123'
>>> 'user1' in passwords
True
>>> passwords['user1'] == 'pass123'
True
>>> del passwords['user1']
>>> passwords['user1'] == 42
Traceback (most recent call last):
    ...
KeyError: 'user1'
>>> list(passwords)
Traceback (most recent call last):
    ...
ValueError: keys and values are not available in plaintext
'''

# FIXME: implement transactions, currently access to DictSubset is not atomar,
# use SQL transactions
# TODO: support namespaces

import bisect
import hashlib
import os
import random

from sqlalchemy import Column, MetaData, Table, select
from sqlalchemy.engine import Engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.types import VARBINARY
import json
import sqlalchemy


class Db(object):
    '''
    >>> s = Db('sqlite:///:memory:', 'test')
    >>> s.add(('mydata', 42))
    >>> s.has(('mydata', 42))
    True
    >>> s.has(('mydata', 123))
    False
    '''
    HASH_LENGTH = 20
    SLOWNESS = 1000

    def __init__(self, connect, namespace=""):
        if isinstance(connect, Engine):
            self._engine = connect
        else:
            self._engine = sqlalchemy.create_engine(connect)
        self._namespace = namespace
        metadata = MetaData()
        self._table = Table('hashes', metadata,
                            Column('hash',
                                   VARBINARY(self.HASH_LENGTH),  # FIXME: hash lengthd eos not trunacte
                                   primary_key=True))
        metadata.create_all(self._engine)

    def _hash(self, message):
        encoded_message = json.dumps([self._namespace, message])
        return hashlib.sha512(encoded_message).digest()

    def add(self, message):
        # print 'add', message
        message_hash = self._hash(message)
        stmt = self._table.insert().values(hash=message_hash)
        try:
            self._engine.execute(stmt)
        except IntegrityError:
            pass

    def has(self, message):
        # print 'has', message
        message_hash = self._hash(message)
        stmt = select([1]).where(self._table.c.hash == message_hash).limit(1)
        return bool(self._engine.execute(stmt).scalar())

    def slow_add(self, message):
        self.add((message, random.randint(0, self.SLOWNESS)))

    def slow_has(self, message):
        for i in range(0, self.SLOWNESS):
            if self.has((message, i)):
                return True
        return False

    def add_dirt(self, hashes_num, generate_rand=os.urandom):
        for i in range(hashes_num):
            rand = generate_rand(self.HASH_LENGTH)
            self.add(rand)


class Counter(object):
    '''
    >>> c = Counter(Db('sqlite:///:memory:'))
    >>> c.incr('hi')
    1
    >>> c.incr('hi')
    2
    >>> c.count('hi')
    2
    >>> c.count('ho')
    0
    '''

    def __init__(self, db):
        self._db = db

    def incr(self, message):
        # as transaction
        count = self.count(message)
        self._db.add(('counter', count, message))
        return count + 1

    def count(self, message):
        db = self._db

        class L(object):
            def __getitem__(self, index):
                if db.has(('counter', index, message)):
                    return 0
                else:
                    return 1
        l = L()
        if l[0]:
            return 0
        high = 1
        while not l[high]:
            high = high * 2
        return bisect.bisect_right(l, 0.5, 0, high)

    def is_null(self, message):
        return not self._db.has(('counter', 0, message))


class CrypledSet(object):
    '''
    >>> s = CrypledSet(Db('sqlite:///:memory:'))
    >>> 'mymsg' in s
    False
    >>> s.add('mymsg')
    >>> 'mymsg' in s
    True
    >>> s.discard('mymsg')
    >>> 'mymsg' in s
    False
    '''
    def __init__(self, db):
        self._counter = Counter(db)

    def _toggle_mark(self, message):
        self._counter.incr(message)

    def add(self, message):
        if message in self:
            return
        self._toggle_mark(message)

    def discard(self, message):
        if message not in self:
            return
        self._toggle_mark(message)

    def __contains__(self, message):
        return self._counter.count(message) % 2 == 1


# used by DictSubset
class EqOnly(object):

    def __init__(self, dict_subset_obj, key):
        self._key = key
        self._dict_subset_obj = dict_subset_obj

    def __eq__(self, value):
        return self._dict_subset_obj._verify(self._key, value)


class DictSubset(object):
    def __init__(self, db, namespace):
        self._db = db
        self._revision_counter = Counter(db)
        self._keys = CrypledSet(db)

    def __setitem__(self, key, value):
        if value is None:
            raise ValueError("value should'nt be None")
        revision = self._revision_counter.incr(key)
        self._db.slow_add(('key-value-pair', revision, key, value))
        self._keys.add(key)

    def __getitem__(self, key):
        if key not in self:
            raise KeyError(key)
        return EqOnly(self, key)

    def _verify(self, key, value):
        revision = self._revision_counter.count(key)
        return self._db.slow_has(('key-value-pair', revision, key, value))

    def __delitem__(self, key):
        self._keys.discard(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        return key in self._keys

    def has_key(self, key):
        return key in self

    def __iter__(self):
        raise ValueError('keys and values are not available in plaintext')


def open(sqlalchemy_connect_string="sqlite:///:memory:", namespace=""):
    db = Db(sqlalchemy_connect_string)
    return DictSubset(db, namespace)


def add_dirt(sqlalchemy_connect_string, dirt):
    pp = Db(sqlalchemy_connect_string)
    pp.add_dirt(dirt)
