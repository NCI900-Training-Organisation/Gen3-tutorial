#!/usr/bin/env python3
"""Verify the entire local login; never print passwords, cookies or tokens."""
from html.parser import HTMLParser
import json
import sys
from urllib.parse import urljoin, urlparse
import requests


class LoginForm(HTMLParser):
    def __init__(self):
        super().__init__()
        self.action = None
        self.fields = {}

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.action = attrs.get('action', '')
        if tag == 'input' and attrs.get('name'):
            self.fields[attrs['name']] = attrs.get('value', '')


password = json.load(sys.stdin)['password']
with requests.Session() as session:
    response = session.get('http://gen3.kind.test/user/login/generic_oidc_idp',
                           params={'redirect': 'http://gen3.kind.test/'}, timeout=30)
    response.raise_for_status()
    form = LoginForm()
    form.feed(response.text)
    if not {'login', 'password'} <= form.fields.keys():
        raise SystemExit('Expected the Dex LDAP login form')
    target = urljoin(response.url, form.action or response.url)
    if urlparse(target).netloc != 'gen3.kind.test':
        raise SystemExit('Refusing to submit credentials to an unexpected host')
    form.fields.update(login='training', password=password)
    response = session.post(target, data=form.fields, timeout=30)
    response.raise_for_status()
    response = session.get('http://gen3.kind.test/user/user', timeout=30)
    response.raise_for_status()
    if response.json().get('username') != 'training':
        raise SystemExit('Gen3 did not authenticate the training account')
print('LDAP, Dex callback and authenticated Gen3 session verified for training.')
