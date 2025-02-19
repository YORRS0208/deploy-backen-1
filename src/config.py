#from decouple import config
import os

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')

class DevelepmentConfig(Config):
    DEBUG = True

config = {
    'development': DevelepmentConfig
}