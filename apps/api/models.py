import os
import time

from django.db import models

from users.models import UserProfile


KEY_SIZE = 18
SECRET_SIZE = 32
VERIFIER_SIZE = 10
CONSUMER_STATES = (
    ('pending', 'Pending'),
    ('accepted', 'Accepted'),
    ('canceled', 'Canceled'),
    ('rejected', 'Rejected')
)
REQUEST_TOKEN = 1
ACCESS_TOKEN = 2
TOKEN_TYPES = ((REQUEST_TOKEN, u'Request'), (ACCESS_TOKEN, u'Access'))


class Access(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()

    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)

    status = models.CharField(max_length=16, choices=CONSUMER_STATES,
                              default='pending')
    user = models.ForeignKey(UserProfile, null=True, blank=True,
                             related_name='drf_consumers')

    class Meta:
        db_table = 'piston_consumer'


class Token(models.Model):
    key = models.CharField(max_length=KEY_SIZE)
    secret = models.CharField(max_length=SECRET_SIZE)
    verifier = models.CharField(max_length=VERIFIER_SIZE)
    token_type = models.IntegerField(choices=TOKEN_TYPES)
    timestamp = models.IntegerField(default=long(time.time()))
    is_approved = models.BooleanField(default=False)

    user = models.ForeignKey(UserProfile, null=True, blank=True,
                             related_name='drf_tokens')
    consumer = models.ForeignKey(Access)

    callback = models.CharField(max_length=255, null=True, blank=True)
    callback_confirmed = models.BooleanField(default=False)

    class Meta:
        db_table = 'piston_token'

    @classmethod
    def generate_new(cls, token_type, creds, user=None):
        return cls.objects.create(
            token_type=token_type,
            consumer=creds,
            key=generate(),
            secret=generate(),
            timestamp=time.time(),
            verifier=generate() if token_type == REQUEST_TOKEN else None,
            user=user)


class Nonce(models.Model):
    token_key = models.CharField(max_length=KEY_SIZE, null=True)
    consumer_key = models.CharField(max_length=KEY_SIZE, null=True)
    key = models.CharField(max_length=255)

    class Meta:
        db_table = 'piston_nonce'
        unique_together = ('token_key', 'consumer_key', 'key')


def generate():
    return os.urandom(64).encode('hex')
