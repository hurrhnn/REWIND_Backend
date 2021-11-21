import os

PATH = os.path.dirname(os.path.abspath(__file__))

SQLALCHEMY_BINDS = {
    'main': f'sqlite:///{PATH}/WIND_main.db',
    'chat': f'sqlite:///{PATH}/WIND_chat.db'
}

del os, PATH
