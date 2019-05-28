# -*- coding: utf-8 -*-

# dependesse: gunicorn, PySocks, pyTelegramBotAPI, requests, urllib3

from telebot import apihelper
from enum import Enum

# key for bot
token = ''
apihelper.proxy = {'https':'socks5://:@:'}


class States(Enum):
    """
    описываем возможные состояния
    """
    S_start = "0"  # Начало нового диалога
    S_cmd_tv = "1"     # Wait ID VM for console
    S_cmd_show_vm = "2" # wait ID VM for show info
    S_live_migrate = "3" # live migrate
    S_get_type_cod = "4" # type COD
    S_server_list = "5" # list_srv
    S_get_tenant_id = "6" # get tenant ID
    S_server = "7" # actions from server
    S_server_start = "8"
    S_server_stop = "9"
    S_server_retart = "10"
    S_server_diag = "11" # Show info from the inside VM
    S_quota_show = "12" # show quote info about HDD, CPU RAM etc. (not Networking)
    S_flavor_create = "13" # Create flavor
    S_flavor_list = "14" # Show list flavor


