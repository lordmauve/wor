# Django settings for dj project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = [
#	('Your name here', 'your-email@example.com'),
]

MANAGERS = ADMINS

DATABASE_ENGINE = ''           # No Django database - using ZODB instead

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'Europe/London'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-gb'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = False

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = '../server_root/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'nba%fbdke^53$*p8+1x1#_0kf@htj9@eisz0ivcm2ji0*olh#4'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'dj.urls'

import os.path
def relpath(p):
	return os.path.abspath(os.path.join(os.path.dirname(__file__), p))

TEMPLATE_DIRS = [
	relpath('templates'),	
]

INSTALLED_APPS = [
	'dj.ui',
]

SESSION_ENGINE = 'django.contrib.sessions.backends.file'

RECAPTCHA_PUBLIC_KEY = '6LcbuAkAAAAAALQmzH9QtfUlskcXva4ClJl28cn_'
RECAPTCHA_PRIVATE_KEY = '6LcbuAkAAAAAAAp69EH8m-W6ABhxPd3Pfzy7I8qL'
