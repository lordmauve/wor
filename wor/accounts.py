import os
import time
import random

try:
    from hashlib import sha1
except ImportError:
    from sha1 import new as sha1


from persistent import Persistent
from persistent.list import PersistentList

from BTrees.OOBTree import OOBTree



class Account(Persistent):
    """A user account"""
    def __init__(self, username, password, realname=None, email=None):
        """Create an account for the username and cleartext password given.

        If realname and email are given they are also stored.
        """
        self.username = username
        self.realname = realname
        self.email = email

        self.pcs = PersistentList() # player characters

        self.set_password(password)

    def __repr__(self):
        return "<Account: %s>" % self.username

    def get_players(self):
        return list(self.pcs)

    def set_password(self, newpassword):
        """Updates the user's password, encrypting it with sha1.

        Salt is drawn from os.urandom()
        """
        salt = os.urandom(3)
        self.password = salt + ':' + sha1(salt + str(newpassword)).digest()

    def check_password(self, supplied_password):
        """Check the supplied password against the stored password.
        Returns True if the passwords match.
        """
        salt, crypt = self.password.split(':')
        return crypt == sha1(salt + str(supplied_password)).digest()

    def create_player(self, name, alignment):
        from wor.db import db
        player = db.world().create_player(name, alignment)
        self.pcs.append(player)


class AuthenticationFailure(Exception):
    """Error signalling the authentication failed."""


class DuplicateUsername(Exception):
    """Error signalling that the username requested was already taken"""


class AccountManager(Persistent):
    """A system for managing accounts and authentication.
    
    """
    def __init__(self):
        self.accounts = OOBTree()   # mapping username -> account

    def authenticate(self, username, password):
        """Authenticate with username and password.
        Returns the corresponding account.

        If no match, raises AuthenticationFailure."""

        try:
            account = self.get_account(username)
        except KeyError:
            account = None

        if account is None or not account.check_password(password):
            time.sleep(random.random()) # avoid leaking information about whether we found the account
            raise AuthenticationFailure(u"The username and password combination were not found.")

        return account

    def is_username_taken(self, username):
        return username.lower() in self.accounts

    def get_account(self, username):
        return self.accounts[username.lower()]

    def create_account(self, username, password, realname=None, email=None):
        """Create an account in this manager and returns the new account.

        Raises DuplicateUsername if the username requested is already taken.

        """
        if self.is_username_taken(username):
            raise DuplicateUsername("The username '%s' is already taken." % username)
        account = Account(username, password, realname, email)
        self.accounts[username.lower()] = account
        return account

    def generate_password(self, chars=12):
        """Generate a random password."""
        valid = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_=+,.<>:;!$%^&*()?/"
        password = ""
        for i in xrange(chars):
            password += random.choice(valid)
        return password
