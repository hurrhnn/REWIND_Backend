import os

PATH = os.path.dirname(os.path.abspath(__file__))

SQLALCHEMY_DATABASE_URI = f'sqlite:///{PATH}/WIND.db'

del os, PATH
