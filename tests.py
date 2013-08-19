#!/usr/bin/env python
# encoding=utf-8

import os
import unittest
os.environ['MYAPP_CONFIG'] = 'tests.cfg'
import application
from myapp.util import redis


class MyappTestCase(unittest.TestCase):

    def setUp(self):
        application.app.config['LANG'] = 'en'
        self.app = application.app.test_client()

    def tearDown(self):
        redis.flushdb()

    def test_root_page(self):
        """Make sure url root(/) is redirect to /home"""
        rv = self.app.get('/')
        assert '302 FOUND' in rv.status
        assert 'Redirecting' in rv.data
        assert '<a href="/home">/home</a>' in rv.data

    def test_home_page(self):
        rv = self.app.get('/home')
        assert '<html lang="en">' in rv.data
        assert 'Please Sign in or <a href="/register">Register</a>.</p>'
        assert 'form id="loginForm"' in rv.data

    def test_register_page(self):
        rv = self.app.get('/register')
        assert '<form class="form-signup" method="post"' in rv.data

    def register(self, userid, email, passwd, passwd2):
        return self.app.post('/register', data=dict(
            id=userid,
            email=email,
            passwd=passwd,
            passwd2=passwd2,
            ), follow_redirects=True)

    def login(self, userid, password):
        return self.app.post('/home', data=dict(
            id=userid,
            passwd=password,
            ), follow_redirects=True)

    def logout(self):
        return self.app.get('/logout', follow_redirects=True)

    def test_register(self):
        rv = self.register('haje01', 'haje01@naver.com', 'asdf', 'asdf')
        assert 'haje01' in rv.data
        assert 'Sign out' in rv.data

        # duplicate userid
        rv = self.register('haje01', 'haje01@naver.com', 'asdf', 'asdf')
        assert 'That ID is already exists' in rv.data

    def test_login(self):
        self.register('haje01', 'haje01@naver.com', 'asdf', 'asdf')
        rv = self.logout()
        assert 'Please Sign in or <a href="/register">Register</a>.</p>'
        rv = self.login('haje01', 'asdf')
        assert 'haje01' in rv.data
        assert 'Sign out' in rv.data

        # wrong id / passwd
        rv = self.logout()
        rv = self.login('haje01', 'asdfx')
        assert 'ID or password mismatch' in rv.data

if __name__ == '__main__':
    unittest.main()
