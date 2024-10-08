"""
Django settings for VehicleRouting project.

Generated by 'django-admin startproject' using Django 5.1.1.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.1/ref/settings/
"""
import environ,os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False)) # set casting, default value
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))



# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.1/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure--=@3f!($xix34^8+nv_5^cc33p95g*#k@m%2#i4#507rx-5c_)'




# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'home',
    'ai_vehicle',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'VehicleRouting.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'VehicleRouting.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.1/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}


# Password validation
# https://docs.djangoproject.com/en/5.1/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/5.1/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

STATIC_URL = 'static/'
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')



# Directory where static files will be collected during production


# Default primary key field type
# https://docs.djangoproject.com/en/5.1/ref/settings/#default-auto-field



STATICFILES_DIRS = [BASE_DIR/'static']

STATIC_ROOT = os.path.join(BASE_DIR,'assets')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# settings.py

# SMTP configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'        # SMTP server host
EMAIL_PORT = 587                     # SMTP port (use 465 for SSL)
EMAIL_USE_TLS = True                 # Use TLS (True) or SSL (False if using SSL)
EMAIL_USE_SSL = False                # Set to True if using SSL (port 465)

EMAIL_HOST_USER     = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASSWORD")

DEFAULT_FROM_EMAIL = env("EMAIL_HOST_USER")  

GEMINI_API_KEY=env("GEMINI_API_KEY")
GOOGLEMAPSKEY=env('GOOGLEMAPSKEY')
FROMLATITUDE=30.706571
FROMLONGITUDE=76.687692


CRONJOBS = [
   ('0 0 * * *', 'home.cron.today_due_emails'),   # every morning at 12:00 AM for due payemnts
   ('0 0 * * *', 'home.cron.due_payments_emails'),   # every morning at 12:00 AM
   ('0 0 * * *', 'home.cron.final_warning_emails'),   # every morning at 12:00 AM
   ('0 0 * * *', 'home.cron.tomorrow_due_emails'),   # every morning at 12:00 AM

]

if int(env("IS_SERVER")): 
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = "/home/root/.config/gcloud/application_default_credentials.json" # for linux