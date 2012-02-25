"""Verify a reCAPTCHA response."""

import urllib
import urllib2
from django.conf import settings


RECAPTCHA_URL = 'http://api-verify.recaptcha.net/verify'

def verify_recaptcha(request):
    try:
        challenge = request.POST['recaptcha_challenge_field']
        response = request.POST['recaptcha_response_field']
    except KeyError:
        return False

    data = {
        'challenge': challenge,
        'response': response,
        'remoteip': request.META.get('REMOTE_ADDR', '0.0.0.0'),
        'privatekey': settings.RECAPTCHA_PRIVATE_KEY
    }
    resp = urllib2.urlopen(getattr(settings, 'RECAPTCHA_URL', RECAPTCHA_URL), urllib.urlencode(data))
    lines = resp.read().split('\n')
    resp.close()
    return lines[0] == 'true'

