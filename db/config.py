import os

PATH = os.path.dirname(os.path.abspath(__file__))

SQLALCHEMY_BINDS = {
    'main': f'sqlite:///{PATH}/WIND_main.db?check_same_thread=False',
    'chat': f'sqlite:///{PATH}/WIND_chat.db?check_same_thread=False'
}

del os, PATH
