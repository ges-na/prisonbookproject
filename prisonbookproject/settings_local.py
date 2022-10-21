from .settings import *

SECRET_KEY = env("SECRET_KEY")

# Database
# https://docs.djangoproject.com/en/4.0/ref/settings/#databases
DATABASES = {"default": env.db()}
