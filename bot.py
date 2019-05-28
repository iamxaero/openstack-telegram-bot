# -*- coding: utf-8 -*-
import telebot
import config
import state
from telebot import types # for keyboard
import opstack
from telebot import util
import bot_logs as bl
import time
import re


# Loging
bl.logger_init()
# name modules
logger = bl.logging.getLogger("bot_telegram")
# level for logs
logger.setLevel(bl.logging.DEBUG)
# Where to send the log stdout for docker
logger.addHandler(bl.logging.StreamHandler(bl.sys.stdout))
# Sent fist message
logger.info("Bot started")

# attache config for telebot
bot = telebot.TeleBot(config.token)

"""
Set in Telegram

tenant - show information about tenant (send tenant name)
console - get url from server console (send server ID)
check_api - check access OpenStack API
hosts - list OpenStack hosts
server_list - show server list (send tenant name)
server_show - show server information (send server ID)
server_diag - show server diagnostic (send server ID)
server_start - start server (send server ID)
server_stop - stop server (send server ID)
server_reboot - reboot server (send server ID)
live_migrate - live-migration active server (send server ID)
quota_show - show tenant quota (send tenant name)
flavor_create - create flavor
flavor_list - show flavor list
access - get access to change state VM
cancel - reset conversation, start over
help - show help
"""

commands = {  # command description used in the "help" command
    'tenant'       : 'show information about tenant (send tenant name)',
    'console'      : 'get url from server console (send server ID)',
    'check_api'    : 'check access OpenStack API',
    'hosts'        : 'list OpenStack hosts',
    'server_list'  : 'show server list (send tenant name)',
    'server_show'  : 'show server information (send server ID)',
    'server_diag'  : 'show server diagnostic (send server ID)',
    'server_start' : 'start server (send server ID)',
    'server_stop'  : 'stop server (send server ID)',
    'server_reboot': 'reboot server (send server ID)',
    'live_migrate' : 'live-migration active server (send server ID)',
    'migrate'      : 'in Development (send server ID)',
    'quota_show'   : 'show tenant quota (send tenant name)',
    'server'       : 'choose server action (send server ID)',
    'flavor_create': 'flavor create',
    'flavor_list'  : 'flavor list',
    'access'       : 'get access to change state VM\n',
    'cancel'       : 'reset conversation, start over',
    'help'         : 'show help'
}


# Handlers match command and set state for user. We have a dict in state.py for save state user.
# TO DO: Next step for coding, send dict in DB
@bot.message_handler(commands=["start", "help"])  # Start conversation
def cmd_start(message):
    logger.info("command start or stop conversation", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    help_text = "<b>You can control me by sending these commands:</b>\n\n"
    for cmd in commands:
        help_text += "/" + cmd + ":  " + "<i>" + commands[cmd] + "</i>" + "\n"
    bot.send_message(message.chat.id, help_text, parse_mode='HTML')


# TO DO: For add users in access list, need DB.
@bot.message_handler(commands=["access"])  # Access like admin
def cmd_start(message):
    logger.info("command show user id telegram", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    bot.send_message(message.chat.id, f"You telegram ID <code>{ message.from_user.id }</code>, send id @iamxaero to get access", parse_mode="HTML")


# check Opstack api
@bot.message_handler(commands=["check_api"])
def check_api(message):
    logger.info("command check api", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    if state.check_admins_id(message.from_user.id):
        answer = opstack.check_api()
        send_large_msg(message.chat.id, "".join(answer))
    else:
        bot.send_message(message.chat.id, "Access denied, if you need access /access")
        logger.warning(f"Access denied {message.from_user.id}",
                       extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})


@bot.message_handler(commands=["console", "tv", "TV"]) # return console url for server
def cmd_tv(message):
    logger.info("command get console", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    # get state for check
    st = state.get_state(message.from_user.id)
    if st == config.States.S_start.value or st is False:
        bot.send_message(message.chat.id, "Send my *ID VM*", parse_mode="Markdown")
        # if state ok, push state in dict and start wrapper
        state.set_state(message.from_user.id, config.States.S_cmd_tv.value)
    elif not st == config.States.S_start.value:
        bot.send_message(message.chat.id, "Complete previous action or reset active command /cancel")
    else:   # Exit to error
        logger.error("err in cmd_tv")


@bot.message_handler(commands=["servers", "server_list"]) # List all server in tenant/project
def server_list(message):
    logger.info("command list all server in tenant/projectd", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    st = state.get_state(message.from_user.id)
    if st == config.States.S_start.value or st is False:
        bot.send_message(message.chat.id, "Ok, send my <code>tenant/project name</code>", parse_mode="HTML")
        state.set_state(message.from_user.id, config.States.S_server_list.value)
    elif not st == config.States.S_start.value:
        bot.send_message(message.chat.id, "Complete previous action or reset active state /cancel")
    else:
        logger.error("error in cmd_show_vm")


# Server diagnostic
@bot.message_handler(commands=["server_diag", "server_diagnostic"])
def server_diagnostic(message):
    logger.info("command server diagnostic", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    st = state.get_state(message.from_user.id)
    if st == config.States.S_start.value or st is False:
        bot.send_message(message.chat.id, "Ok, send my <code>server ID</code>", parse_mode="HTML")
        state.set_state(message.from_user.id, config.States.S_server_diag.value)
    elif not st == config.States.S_start.value:
        bot.send_message(message.chat.id, "Complete previous action or reset active state /cancel")
    else:
        logger.error("error in server_diagnostic")


# Quota show
@bot.message_handler(commands=["quota_show"])
def quota_show(message):
    logger.info("command show quota", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    st = state.get_state(message.from_user.id)
    if st == config.States.S_start.value or st is False:
        bot.send_message(message.chat.id, "Ok, send my <code>tenant name</code>", parse_mode="HTML")
        state.set_state(message.from_user.id, config.States.S_quota_show.value)
    elif not st == config.States.S_start.value:
        bot.send_message(message.chat.id, "Complete previous action or reset active state /cancel")
    else:
        logger.error("error in server_diagnostic")


# return id tenant
@bot.message_handler(commands=["get", "get_id"])
def get_id(message):
    logger.info("command show tenant id", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    if state.check_admins_id(message.from_user.id):
        st = state.get_state(message.from_user.id)
        if st == config.States.S_start.value or st is False:
            bot.send_message(message.chat.id, "Ok, send my `tenant/project name`", parse_mode="Markdown")
            state.set_state(message.from_user.id, config.States.S_get_tenant_id.value)
        elif not st == config.States.S_start.value:
            bot.send_message(message.chat.id, "Complete previous action or reset active state /cancel")
        else:
            logger.error("error in get_id")
    else:
        bot.send_message(message.chat.id, "Access denied, if you need access /access")
        logger.warning(f"Access denied {message.from_user.id}",
                       extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})


# create flavor
@bot.message_handler(commands=["flavor_create"])
def get_id(message):
    logger.info("command create flavor", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    if state.check_admins_id(message.from_user.id):
        st = state.get_state(message.from_user.id)
        if st == config.States.S_start.value or st is False:
            send_large_msg(message.chat.id, f"get info about flavor, for exemple: i43,2,16")
            state.set_state(message.from_user.id, config.States.S_flavor_create.value)
        elif not st == config.States.S_start.value:
            bot.send_message(message.chat.id, "Complete previous action or reset active state /cancel")
        else:
            logger.error("error in get_id")
    else:
        bot.send_message(message.chat.id, "Access denied, if you need access /access")
        logger.warning(f"Access denied {message.from_user.id}",
                       extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})


# flavor list 
@bot.message_handler(commands=["flavor_list"])
def flavor_list(message):
    logger.info("command flavor list", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    callback_button1 = types.InlineKeyboardButton(text="i01", callback_data=f"i01 {message.from_user.id}")
    callback_button2 = types.InlineKeyboardButton(text="i02", callback_data=f"i02 {message.from_user.id}")
    callback_button3 = types.InlineKeyboardButton(text="i03", callback_data=f"i03 {message.from_user.id}")
    callback_button4 = types.InlineKeyboardButton(text="i04", callback_data=f"i04 {message.from_user.id}")
    callback_button5 = types.InlineKeyboardButton(text="i04", callback_data=f"i05 {message.from_user.id}")
    callback_button6 = types.InlineKeyboardButton(text="i05", callback_data=f"i06 {message.from_user.id}")
    keyboard.add(callback_button1, callback_button2, callback_button3, callback_button4, callback_button5,
                 callback_button6)
    bot.send_message(message.chat.id, "choose action:", reply_markup=keyboard)
    state.set_state(message.from_user.id, config.States.S_start.value)
    logger.info("response keybord action server")


# host list ("i43", "i03", "i04", "i42", "i34", "i34r")
@bot.message_handler(commands=["hosts"])
def host_list(message):
    if state.check_admins_id(message.from_user.id):
        logger.info("command host list", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        callback_button1 = types.InlineKeyboardButton(text="i01", callback_data=f"i01_host {message.from_user.id}")
        callback_button2 = types.InlineKeyboardButton(text="i02", callback_data=f"i02_host {message.from_user.id}")
        callback_button3 = types.InlineKeyboardButton(text="i03", callback_data=f"i03_host {message.from_user.id}")
        callback_button4 = types.InlineKeyboardButton(text="i04", callback_data=f"i04_host {message.from_user.id}")
        callback_button5 = types.InlineKeyboardButton(text="i05", callback_data=f"i05_host {message.from_user.id}")
        callback_button6 = types.InlineKeyboardButton(text="i06", callback_data=f"i06_host {message.from_user.id}")
        keyboard.add(callback_button1, callback_button2, callback_button3, callback_button4, callback_button5,
                     callback_button6)
        bot.send_message(message.chat.id, "choose action:", reply_markup=keyboard)
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response keybord action server")
    else:
        bot.send_message(message.chat.id, "Access denied, if you need access /access")
        logger.warning(f"Access denied {message.from_user.id}",
                       extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})


# live migrate VM (only admin)
@bot.message_handler(commands=["live_migrate", "live-migrate"])
def cmd_live_migrate(message):
    if state.check_admins_id(message.from_user.id): # Check access
        logger.info("command live migrate", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
        st = state.get_state(message.from_user.id)
        if st == config.States.S_start.value or st is False:
            bot.send_message(message.chat.id, "Ok, i show it, give my ID VM")
            state.set_state(message.from_user.id, config.States.S_live_migrate.value)
        elif not st == config.States.S_start.value:
            bot.send_message(message.chat.id, "Complete previous action or reset active command /cancel")
        else:
            logger.error("error in cmd_live_migrate")
    else:
        bot.send_message(message.chat.id, "Access denied, if you need access /access")
        logger.warning(f"Access denied {message.from_user.id}",
                       extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})


# return information about the project
@bot.message_handler(commands=["project", "tenant"])
def cmd_get_type_cod(message):
    logger.info("command show info about tenant", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    st = state.get_state(message.from_user.id)
   if st == config.States.S_start.value or st is False:
        bot.send_message(message.chat.id, "Ok, send my tenant/project name")
        state.set_state(message.from_user.id, config.States.S_get_type_cod.value)
    elif not st == config.States.S_start.value:
        bot.send_message(message.chat.id, "Complete previous action or reset active state /cancel")
    else:
        logger.error("error in get_type_cod")


# /reset state conversation
@bot.message_handler(commands=["reset", "cancel"])
def cmd_reset(message):
    logger.info("command reset state conversation", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    bot.send_message(message.chat.id, "Active command to cancel")
    state.set_state(message.from_user.id, config.States.S_start.value)
    state.del_id_vm(message.from_user.id)


# show VM/server info
@bot.message_handler(commands=["show", "show_vm","server_show"])
def cmd_show_vm(message):
    logger.info("command show VM/server info", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    st = state.get_state(message.from_user.id)
    # it's block a code, need to for show status VM after action with VM
    try:
        # after migrate (for exemple) we set state in dict (id_vm = {})
        # and command show will be return us state many times
        srv_id = state.get_id_vm(message.from_user.id)
        if len(srv_id) == 36:
            recording = 1
        else:
            recording = 0
    except:
        recording = 0
    if recording == 1:
        answer = opstack.bot_show_vm(state.get_id_vm(message.from_user.id))
        bot.send_message(message.chat.id, f"I remember you chose: <code>{srv_id}</code>", parse_mode="HTML")
        send_large_msg(message.chat.id, "".join(answer))
        bot.send_message(message.chat.id, f"if you have to choose a new server /cancel or repeat /show", parse_mode="HTML")
    elif st == config.States.S_start.value or st is False:
        bot.send_message(message.chat.id, "Ok, i show it, give my ID VM")
        state.set_state(message.from_user.id, config.States.S_cmd_show_vm.value)
    elif not st == config.States.S_start.value:
        bot.send_message(message.chat.id, "Complete previous action or reset active command /cancel")
    else:
        logger.error("error in cmd_show_vm")


# stop server (only admin)
@bot.message_handler(commands=["stop_vm", "stop", "server_stop"])
def cmd_stop_vm(message):
    logger.info("command stop server", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    if state.check_admins_id(message.from_user.id):  # Check access
        st = state.get_state(message.from_user.id)
        if st == config.States.S_start.value or st is False:
            bot.send_message(message.chat.id, "Ok, i do it, give my server ID")
            state.set_state(message.from_user.id, config.States.S_server_stop.value)
        elif not st == config.States.S_start.value:
            bot.send_message(message.chat.id, "Complete previous action or reset active command /cancel")
        else:
            logger.error("error in cmd_show_vm")
    else:
        bot.send_message(message.chat.id, "Access denied, if you need access /access")
        logger.warning(f"Access denied {message.from_user.id}",
                       extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})


# start server (only admin)
@bot.message_handler(commands=["start_vm", "server_start"])
def cmd_start_vm(message):
    logger.info("command start server", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    if state.check_admins_id(message.from_user.id):  # Check access
        st = state.get_state(message.from_user.id)
        if st == config.States.S_start.value or st is False:
            bot.send_message(message.chat.id, "Ok, i do it, give my server ID")
            state.set_state(message.from_user.id, config.States.S_server_start.value)
        elif not st == config.States.S_start.value:
            bot.send_message(message.chat.id, "Complete previous action or reset active command /cancel")
        else:
            logger.error("error in cmd_show_vm")
    else:
        bot.send_message(message.chat.id, "Access denied, if you need access /access")
        logger.warning(f"Access denied {message.from_user.id}",
                       extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})

# reboot server (only admin)
@bot.message_handler(commands=["reboot_vm", "reboot", "server_reboot"])
def cmd_hard_reboot_vm(message):
    logger.info("command reboot server", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    if state.check_admins_id(message.from_user.id):  # Check access
        st = state.get_state(message.from_user.id)
        if st == config.States.S_start.value or st is False:
            bot.send_message(message.chat.id, "Ok, i do it, give my server ID")
            state.set_state(message.from_user.id, config.States.S_server_retart.value)
        elif not st == config.States.S_start.value:
            bot.send_message(message.chat.id, "Complete previous action or reset active command /cancel")
        else:
            logger.error("error in cmd_show_vm")
    else:
        bot.send_message(message.chat.id, "Access denied, if you need access /access")
        logger.warning(f"Access denied {message.from_user.id}",
                       extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})

# server action
# TO DO access in commands
@bot.message_handler(commands=["server"])
def cmd_server(message):
    logger.info("command server action", extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})
    if state.check_admins_id(message.from_user.id):  # Check access
        st = state.get_state(message.from_user.id)
        if st == config.States.S_start.value or st not in locals():
            bot.send_message(message.chat.id, "Send me server ID")
            state.set_state(message.from_user.id, config.States.S_server.value)
        elif not st == config.States.S_start.value:
            bot.send_message(message.chat.id, "Complete previous action or reset active command /cancel")
        else:
            logger.error("error in cmd_server")
    else:
        bot.send_message(message.chat.id, "Access denied, if you need access /access")
        logger.warning(f"Access denied {message.from_user.id}",
                       extra={'bot': {'chat_id': message.chat.id, 'user_id': message.from_user.id}})

'''
Wraps mach param after bot commands

After we set state VM, we needed mach server ID or tenant name.
Below code takes users messages, checking it and if all right to send param in opanstack.py
'''


# flavor create
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_flavor_create.value)
def flavar_param(message):
    if opstack.normalize_flavor_param(message.text) is not None:
        # send request for create
        requst = opstack.normalize_flavor_param(message.text)
        answer = opstack.flavor_create(requst[0],requst[1],requst[2])
        # send answer in function for division into parts
        send_large_msg(message.chat.id, answer)
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info(f"create flavor{answer}")


# Console
# check state status
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_cmd_tv.value)
def user_entering_idvm(message):
    # send messages in normalazer
    if opstack.normalize_server_id(message.text) is not None:
        # get normalized param
        srv_id = opstack.normalize_server_id(message.text)
        # set state id VM for show command
        state.set_id_vm(message.from_user.id, srv_id)
        # send request in openstack
        rez = opstack.bot_ops_url(state.get_id_vm(message.from_user.id))
        # send answer in function for division into parts
        send_large_msg(message.chat.id, rez)
        # reset user state in start position
        state.set_state(message.from_user.id, config.States.S_start.value)
        # send log about request
        logger.info("response console")


# Portality. Attention, for this command we have two request. first in portal, second in openstack
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_get_type_cod.value)
def user_entering_idvm(message):
    if opstack.normalize_tenent_name(message.text) is not None:
        get_name = opstack.normalize_tenent_name(message.text)
        result = opstack.bot_get_type_env(get_name)
        tenant_id = opstack.bot_get_tenant_id(get_name)
        send_large_msg(message.chat.id, f"{result}\nTenant ID: <code>{tenant_id}</code>")
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response info tenant")


# Show VM
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_cmd_show_vm.value)
def user_entering_idvm(message):
    if opstack.normalize_server_id(message.text) is not None:
        srv_id = opstack.normalize_server_id(message.text)
        state.set_id_vm(message.from_user.id, srv_id)
        answer = opstack.bot_show_vm(state.get_id_vm(message.from_user.id))
        send_large_msg(message.chat.id, "".join(answer))
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response show vm")


# Quota Show
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_quota_show.value)
def user_entering_idtenant(message):
    if opstack.normalize_tenent_name(message.text) is not None:
        get_name = opstack.normalize_tenent_name(message.text)
        answer = opstack.bot_qoute_show(get_name)
        send_large_msg(message.chat.id, "".join(answer))
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response show quota")


# Show diagnostic information about server
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_server_diag.value)
def user_entering_idvm(message):
    if opstack.normalize_server_id(message.text) is not None:
        srv_id = opstack.normalize_server_id(message.text)
        state.set_id_vm(message.from_user.id, srv_id)
        answer = opstack.bot_diagnostic(state.get_id_vm(message.from_user.id))
        send_large_msg(message.chat.id, "".join(answer))
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response diag server")


# Server list
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_server_list.value)
def user_entering_idtenant(message):
    if opstack.normalize_tenent_name(message.text) is not None:
        get_name = opstack.normalize_tenent_name(message.text)
        answer = opstack.bot_server_list(get_name)
        send_large_msg(message.chat.id, "".join(answer))
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response server list")


# ID project
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_get_tenant_id.value)
def user_entering_idtenant(message):
    if opstack.normalize_tenent_name(message.text) is not None:
        get_name = opstack.normalize_tenent_name(message.text)
        answer = opstack.bot_get_tenant_id(get_name)
        bot.send_message(message.chat.id, f"Tenant ID: {answer}")
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response id tenant")


# Migrate
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_live_migrate.value)
def user_entering_idvm(message):
    if opstack.normalize_server_id(message.text) is not None:
        srv_id = opstack.normalize_server_id(message.text)
        state.set_id_vm(message.from_user.id, srv_id)
        rez = opstack.bot_live_migrate(state.get_id_vm(message.from_user.id))
        send_large_msg(message.chat.id, rez)
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response migrate vm")


# wrap stop
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_server_stop.value)
def user_entering_idvm(message):
    if opstack.normalize_server_id(message.text) is not None:
        srv_id = opstack.normalize_server_id(message.text)
        state.set_id_vm(message.from_user.id, srv_id)
        rez = opstack.bot_stop_srv(state.get_id_vm(message.from_user.id))
        send_large_msg(message.chat.id, rez)
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response stop vm")


# wrap start
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_server_start.value)
def user_entering_idvm(message):
    if opstack.normalize_server_id(message.text) is not None:
        srv_id = opstack.normalize_server_id(message.text)
        state.set_id_vm(message.from_user.id, srv_id)
        rez = opstack.bot_start_srv(state.get_id_vm(message.from_user.id))
        send_large_msg(message.chat.id, rez)
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response start vm")


# wrap reboot
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_server_retart.value)
def user_entering_idvm(message):
    if opstack.normalize_server_id(message.text) is not None:
        srv_id = opstack.normalize_server_id(message.text)
        state.set_id_vm(message.from_user.id, srv_id)
        rez = opstack.bot_reboot_srv(state.get_id_vm(message.from_user.id))
        send_large_msg(message.chat.id, rez)
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response reboot vm")


# Actions server
@bot.message_handler(func=lambda message: state.get_state(message.from_user.id) == config.States.S_server.value)
def user_entering_action(message):
    if opstack.normalize_server_id(message.text) is not None:
        srv_id = opstack.normalize_server_id(message.text)
        state.set_id_vm(message.from_user.id, srv_id)
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        callback_button1 = types.InlineKeyboardButton(text="show", callback_data=f"show {message.from_user.id}")
        callback_button2 = types.InlineKeyboardButton(text="console", callback_data=f"console {message.from_user.id}")
        callback_button3 = types.InlineKeyboardButton(text="start", callback_data=f"start {message.from_user.id}")
        callback_button4 = types.InlineKeyboardButton(text="stop", callback_data=f"stop {message.from_user.id}")
        callback_button5 = types.InlineKeyboardButton(text="reboot", callback_data=f"reboot {message.from_user.id}")
        callback_button6 = types.InlineKeyboardButton(text="live migrate", callback_data=f"live_migrate {message.from_user.id}")
        keyboard.add(callback_button1, callback_button2, callback_button3, callback_button4, callback_button5, callback_button6)
        bot.send_message(message.chat.id, "choose action:", reply_markup=keyboard)
        state.set_state(message.from_user.id, config.States.S_start.value)
        logger.info("response keybord action server")
    else:
        bot.send_message(message.chat.id, "Complete previous action or reset active command /cancel")


# call back with buttons
@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    result = call.data.split(" ")
    if result[0] == "show":
        answer = opstack.bot_show_vm(state.get_id_vm(int(result[1])))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=answer)
        logger.info("response show server")
    if result[0] == "live_migrate":
        answer = opstack.bot_live_migrate(state.get_id_vm(int(result[1])))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=answer)
        logger.info("response live migrate server")
    if result[0] == "console":
        answer = opstack.bot_ops_url(state.get_id_vm(int(result[1])))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=answer)
        logger.info("response console server")
    if result[0] == "stop":
        answer = opstack.bot_stop_srv(state.get_id_vm(int(result[1])))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=answer)
        logger.info("response stop server")
    if result[0] == "start":
        answer = opstack.bot_start_srv(state.get_id_vm(int(result[1])))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=answer)
        logger.info("response start server")
    if result[0] == "reboot":
        answer = opstack.bot_reboot_srv(state.get_id_vm(int(result[1])))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=answer)
        logger.info("response reboot server")
    if result[0]=="i01":
        answer = opstack.flavor_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'flavor list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response flavor list {result[0]}")
    if result[0]=="i02":
        answer = opstack.flavor_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'flavor list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response flavor list {result[0]}")
    if result[0]=="i03":
        answer = opstack.flavor_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'flavor list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response flavor list {result[0]}")
    if result[0]=="i04":
        answer = opstack.flavor_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'flavor list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response flavor list {result[0]}")
    if result[0]=="i05":
        answer = opstack.flavor_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'flavor list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response flavor list {result[0]}")
    if result[0]=="i06":
        answer = opstack.flavor_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'flavor list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response flavor list {result[0]}")
    #host list
    if result[0]=="i01_host":
        result = result[0].split("_")
        answer = opstack.host_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'host list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response host list {result[0]}")
    if result[0]=="i02_host":
        result = result[0].split("_")
        answer = opstack.host_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'host list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response host list {result[0]}")
    if result[0]=="i03_host":
        result = result[0].split("_")
        answer = opstack.host_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'host list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response host list {result[0]}")
    if result[0]=="i04_host":
        result = result[0].split("_")
        answer = opstack.host_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'host list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response host list {result[0]}")
    if result[0]=="i05_host":
        result = result[0].split("_")
        answer = opstack.host_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'host list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response host list {result[0]}")
    if result[0]=="i06_host":
        result = result[0].split("_")
        answer = opstack.host_list(str(result[0]))
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id, text=f'host list in {result[0]}')
        send_large_msg(call.message.chat.id, "".join(answer))
        logger.info(f"response host list {result[0]}")


# it's function for sending large text messages
def send_large_msg(chat_id, msg):
    '''
    Markdown style (it's have a strong character limit ):
    to use this mode, pass Markdown in the parse_mode when using sendMesage.
    Use the following syntax in your message.
    *bolt text*
    _italic text_
    [inline URL](http://www.google.com)
    [inline mention of a user](tg://user?id=123456)
    `inline fixed-width code`
    ``` block_language
    pre-formatted  fixed-width code block
    ```

    HTML style (has a lite character limit)
    <b>bolt</b>
    <i>italic text</i>
    <a href="http://www.google.com">inline URL</a>
    <a href="tg://user?id=123456">inline mention of a user</a>
    <code>inline fixed-width</code>
    <pre>pre-formatted  fixed-width code block</pre>
    '''
    # split into pieces incoming messtages
    splited_msg = util.split_string(msg, 4000)
    # in cycle send answer in piece
    for txt in splited_msg:
        # Parse mod HTML need for beauty output in telegram )))
        try:
            bot.send_message(chat_id, txt, parse_mode="HTML")
        except:
            txt = txt.replace("<code>", " ")
            txt = txt.replace("</code>", " ")
            bot.send_message(chat_id, txt, parse_mode="HTML")


# it's stating bot in none stop
if __name__ == '__main__':

    bot.polling(none_stop=True)

