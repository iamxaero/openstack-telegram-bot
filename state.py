# -*- coding: utf-8 -*-

import config
import bot_logs as bl

state = {}
id_vm = {}
tenant_id = {}
admins_id = ['', '']  # only str!!!!

# logging section
bl.logger_init()
logger = bl.logging.getLogger("state")
logger.setLevel(bl.logging.DEBUG)
logger.addHandler(bl.logging.StreamHandler(bl.sys.stdout))

# Пытаемся узнать «состояние» пользователя
def get_state(user_id):
    global state
    if state.get(user_id):
        return state.get(user_id)
    #    for key, value in state.items():
    #        if key == user_id:
    #            return value
    else:
        return config.States.S_start.value


# Сохраняем текущее «состояние» пользователя в нашу базу
def set_state(user_id, value):
    global state
    if user_id and value:
        state.update({user_id: value})
        return True
    else:
        return False


def set_id_vm(user_id, value):
    global id_vm
    if user_id and value:
        id_vm.update(({user_id: value}))
        return True
    else:
        return False


def del_id_vm (user_id):
    global id_vm
    try:
        id_vm.pop(user_id)
    except:
        pass


def get_id_vm(user_id):
    global id_vm
    if id_vm.get(user_id):
        return id_vm.get(user_id)
    else:
        return False


def check_admins_id(telega_id):
    global admins_id
    if str(telega_id) in admins_id:
        return True
    if str(telega_id) not in admins_id:
        return False
    else:
        logger.error("error in check telegram id")
        return False
