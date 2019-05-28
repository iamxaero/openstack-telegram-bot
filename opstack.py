from keystoneclient.v2_0 import client as keyclient
import novaclient.client as novaclient
import novaclient.utils as novautils
import novaclient.v2.flavors as novaflavor
import keystoneauth1.identity.v2 as keystone_auth
import keystoneauth1.session as session
import cinderclient.client as cinderclient
import cinderclient.utils as cinderutils
import requests
import json
import re
import bot_logs as bl

# logging section
bl.logger_init()
logger = bl.logging.getLogger("processing OpenStack")
logger.setLevel(bl.logging.DEBUG)
logger.addHandler(bl.logging.StreamHandler(bl.sys.stdout))

# list with RT COD
regions = ["i01", "i02", "i03", "i04", "i05", "i06"]


# all env for connect api openstack
def region_env(name, tenant_name=None):
    if name=='i01':
        OS_TENANT_NAME = 'openstack'
        OS_USERNAME = 'admin'
        OS_PASSWORD = 'admin'
        OS_AUTH_URL = 'http://'
    elif name=='i02':
        OS_TENANT_NAME = 'openstack'
        OS_USERNAME = 'admin'
        OS_PASSWORD = 'admin'
        OS_AUTH_URL = 'http://'
    elif name=='i03':
        OS_TENANT_NAME = 'openstack'
        OS_USERNAME = 'admin'
        OS_PASSWORD = 'admin'
        OS_AUTH_URL = 'http://'
    elif name=='i04':
        OS_TENANT_NAME = 'openstack'
        OS_USERNAME = 'admin'
        OS_PASSWORD = 'admin'
        OS_AUTH_URL = 'http://'
    elif name=='i05':
        OS_TENANT_NAME = 'openstack'
        OS_USERNAME = 'admin'
        OS_PASSWORD = 'admin'
        OS_AUTH_URL = 'http://'
    elif name=='i06':
        OS_TENANT_NAME = 'openstack'
        OS_USERNAME = 'admin'
        OS_PASSWORD = 'admin'
        OS_AUTH_URL = 'http://'
    else:
        text.append(f"Place is not defined")

    if tenant_name is None:
        auth = keystone_auth.Password(
            username=OS_USERNAME,
            tenant_name=OS_TENANT_NAME,
            auth_url=OS_AUTH_URL,
            password=OS_PASSWORD,
        )
    # need for show information from users
    if tenant_name is not None:
        auth = keystone_auth.Password(
            username=OS_USERNAME,
            tenant_name=tenant_name,
            auth_url=OS_AUTH_URL,
            password=OS_PASSWORD,
        )
    # trying connection in keystone
    try:
        sess = session.Session(auth=auth)
    except Exception as ff:
        logger.exception(ff)
    return sess


#check api
def check_api():
    answer = []
    for reg in regions:
        try:
            sess = region_env(reg)
            nova = novaclient.Client(version="2.0", session=sess)
            request = nova.services.list()
            answer.append(f"{reg} is UP\n")
        except:
            answer.append(f"{reg} is DOWN\n")
    return answer


# Host list
def host_list(reg):
    answer = []
    sess = region_env(reg)
    nova = novaclient.Client(version="2.0", session=sess)
    num = 1
    try:
        servs = nova.services.list()
        for serv in servs:
            answer.append(f"{num}. HOST: <code>{serv.host}</code>  ROLE: {serv.binary}\n STATUS: {serv.status}  STATE: {serv.state}\n ZONE: {serv.zone}  Disabled reason: {serv.disabled_reason}\n")
            num += 1
        return answer
        logger.info(answer)
    except Exception as ff:
        logger.exception(ff)
        answer.append("i don't know why, but i can't. try \check_api")
        return answer
        logger.info(answer)


# get console
def bot_ops_url(id_vm):
    # get DC in cycle
    for reg in regions:
        try:
            # connect in keystone
            sess = region_env(reg)
            # connect in nova
            nova = novaclient.Client(version="2.0", session=sess)
            try:
                # send request in OpenStack
                url_request = nova.servers.get_console_url(id_vm, console_type='novnc')
                # prepare the result
                url = url_request['console']['url']
                return url
            except:
                # if you choose the wrong DC, choose next one
                continue
        except Exception as ff:
            # if we dont connect in the choose DC, write log and choose next DC
            logger.exception(ff)
            continue
    # Dont found information
    url = "I can not get the console, check ID server and try again"
    return url


# flavor list
def flavor_list(reg_name):
    sess = region_env(reg_name)
    nova = novaclient.Client(version="2.0", session=sess)
    result = []
    num = 1
    try:
        flavors = nova.flavors.list()
        for flavor in flavors:
            result.append(f" {num}. Name: {flavor.name} (<code>{flavor.id}</code>)\nvCPU: {flavor.vcpus} RAM: {flavor.ram} Disk: {flavor.disk} Public: {flavor._info['os-flavor-access:is_public']}\n")
            num += 1
        logger.info(result)
        return result
    except Exception as ff:
        logger.exception(ff)
        result = f"i can't get flavor list"
    return result

# flavor create
def flavor_create(reg_name, vcpu, ram):
    sess = region_env(reg_name)
    nova = novaclient.Client(version="2.0", session=sess)
    flavors = nova.flavors.list()
    flavor_new = f"cpu_{vcpu}_ram_{ram}g"
    ram = int(ram)*1024
    for flavor in flavors:
        if flavor.name == flavor_new:
            result = f"already exists: name <code>{flavor.name}</code>, id <code>{flavor.id}</code>"
            return result
        else:
            continue
    # create new flavor
    try:
        req = nova.flavors.create(name=flavor_new, vcpus=vcpu, disk=0, ram=ram)
        result = f"i'm create flavor.\nName: <code>{req.name}</code> id: <code>{req.id}</code>"
        logger.info(result)
    except Exception as ff:
        logger.exception(ff)
        result = f"i can't create flavor"
    return result


"""
        def create(self, name, ram, vcpus, disk, flavorid="auto",
               ephemeral=0, swap=0, rxtx_factor=1.0, is_public=True,
               description=None):
There is the method "set_keys(metadata)" in novaclient.v2.flavors.Flavor class.
I think you can use it to update metadata

new_flavor = nova_client.flavors.create(name='test2',
                                        ram=512,
                                        vcpus=1,
                                        disk=1000,
                                        flavorid='auto',
                                        ephemeral=0,
                                        swap=0,
                                        rxtx_factor=1.0,
                                        is_public=True)
new_flavor.set_keys(metadata)
where metadata is a dict of key/value pairs to be set.

p.s. The method "create( )" will return the Flavor object.
"""


def bot_show_vm(id_vm):
    """
    all info about VM need format info for telegram
    print(dir([url_request]))
    print(type(url_request))
    print(vars(url_request))
    """
    result = []  # its list filling up in the processing and to return like an answer
    for reg in regions:
        try:
            sess = region_env(reg)
            nova = novaclient.Client(version=2, session=sess)
            try:
                url_request = nova.servers.get(id_vm)
                url_request = url_request._info
                # Processing the response to be sent to the bot
                for key in url_request:
                    # processing dict with volumes
                    if isinstance(url_request[key], list):
                        if key=='os-extended-volumes:volumes_attached':
                            vol = ""
                            try:
                                for vi in url_request[key]:
                                    vol += "    id=" + "<code>" + vi['id'] + "</code>\n"
                                result.append(f"<b>{key}</b>:\n{vol}")
                            except:
                                result.append("something is wrong in the storage")
                                continue
                    # processing dict with network
                    elif isinstance(url_request[key], dict):
                        if key=='addresses':
                            net = ""
                            try:
                                # processing to the network dict
                                for kk in url_request[key]:
                                    net += "<b>Network: " + str(kk) + "</b>\n"
                                    for kk5 in url_request[key][kk]:
                                        for kk2, kk3 in kk5.items():
                                            net += "<i>     " + str(kk2) + ": " + str(kk3) + "</i>\n"
                                result.append(f"{net}")
                            except:
                                result.append("something is wrong in the network")
                                continue
                        # processing dict with flavor
                        elif key=='flavor':
                            try:
                                result.append(f"{key} id : <code>{url_request['flavor']['id']}</code>\n")
                            except:
                                result.append(f"{key}_id : undefined\n")
                    elif isinstance(url_request[key], str):
                        result.append(f"{key}: <code>{url_request[key]}</code>\n")
                    elif isinstance(url_request[key], int):
                        result.append(f"{key}: {url_request[key]}\n")
                    elif url_request[key] is None:
                        result.append(f"{key}: {url_request[key]}\n")
                    else:
                        logger.error(f"it's impossible, but what something happened with the bot_show_vm {key}")
                return sorted(result)
            except:
                continue
        except Exception as ff:
            logger.exception(ff)
            continue
    result.append("\n<b>I can not show information about server</b>")
    return result


def bot_live_migrate(id_vm):
    for reg in regions:
        try:
            sess = region_env(reg)
            nova = novaclient.Client(version="2.0", session=sess)
            try:
                # looking for on what site VM
                url_request = nova.servers.get(id_vm)
                if url_request.id==id_vm:
                    # We found VM and send command to change a state in a migrate
                    nova.servers.live_migrate(id_vm, host=None, block_migration=False, disk_over_commit=False)
                    url = "Server Migrating, for more information /show_vm"
                    return url
                else:
                    continue
            except:
                continue
        except Exception as ff:
            logger.exception(ff)
            continue
    url = "I can't find VM, check ID server and try again"
    return url


def bot_stop_srv(id_vm):
    for reg in regions:
        try:
            sess = region_env(reg)
            nova = novaclient.Client(version="2.0", session=sess)
            try:
                # looking for on what site VM
                url_request = nova.servers.get(id_vm)
                if url_request.id==id_vm:
                    nova.servers.stop(id_vm)
                    url = "Server stopping, for more information /show_vm"
                    return url
                else:
                    continue
            except:
                continue
        except Exception as ff:
            logger.exception(ff)
            continue
    url = "I can't find VM, check ID server and try again"
    return url


def bot_start_srv(id_vm):
    for reg in regions:
        try:
            sess = region_env(reg)
            nova = novaclient.Client(version="2.0", session=sess)
            try:
                # looking for on what site VM
                url_request = nova.servers.get(id_vm)
                if url_request.id==id_vm:
                    nova.servers.start(id_vm)
                    url = "Server starting, for more information /show_vm"
                    return url
                else:
                    continue
            except:
                continue
        except Exception as ff:
            logger.exception(ff)
            continue
    url = "I can't find VM, check ID server and try again"
    return url


def bot_reboot_srv(id_vm):
    for reg in regions:
        try:
            sess = region_env(reg)
            nova = novaclient.Client(version="2.0", session=sess)
            try:
                # looking for on what site VM
                url_request = nova.servers.get(id_vm)
                if url_request.id==id_vm:
                    nova.servers.reboot(id_vm)
                    url = "Server Rebooting, for more information /show_vm"
                    return url
                else:
                    continue
            except:
                continue
        except Exception as ff:
            logger.exception(ff)
            continue
    url = "I can't find VM, check ID server and try again"
    return url


# Collecting information about project
def bot_get_type_env(prj_name):
    prj_name = re.findall('\d+', prj_name)  # get a number in the tenant name
    url = ''  # this is the portality address
    header = {'Content-Type': 'application/json', 'User-Agent': 'curl/7.54.0'}  # set Header for request
    data = {'requester': 'warp_bfa509567134dda600505219bfa05056', 'id': prj_name}  # set Date for request
    try:
        # send request
        request = requests.post(url, json=data, headers=header)
        # response from the portal
        data_portal = json.loads(request.text)
        txt = " (не определен тип UI)"
        logger.info(data_portal[0]['type'])
        if data_portal[0]['type']=='xvdc':
            txt = " (есть доступ к Horizon)"
        elif data_portal[0]['type']=='vdc':
            txt = " (доступ только через portality)"
        # preparing an answer for the user
        rez = "Type UI: " + "<b>" + data_portal[0]['type'] + "</b>" + txt + "\r\nDC: " + "<b>" + \
              data_portal[0]['attrs']['region'] + "</b>"
        return rez
    except:
        rez = "I could not find your project"
        return rez


def bot_server_list(tenant_name):
    bot_answer = []
    num = 1
    for reg in regions:
        try:
            sess = region_env(reg, tenant_name=tenant_name)
            nova = novaclient.Client(version="2.0", session=sess)
            try:
                # send request in the Openstack
                url_request = nova.servers.list(detailed=True)
                # preparing an answer
                for i in url_request:
                    bot_answer.append(f" {num}. {i.name} ({i.status})\n<code>{i.id}</code> \n")
                    num += 1
                return bot_answer
            except:
                continue
        except Exception as ff:
            logger.exception(ff)
            continue
    else:
        bot_answer = "Search results: fail"
        return bot_answer


def bot_get_tenant_id(tenant_name):
    for reg in regions:
        try:
            sess = region_env(reg)
            keystone = keyclient.Client(session=sess)
            tenant_dict = {t.name: t.id for t in keystone.tenants.list()}
            if tenant_dict.get(tenant_name):
                return tenant_dict.get(tenant_name)
            else:
                continue
        except Exception as ff:
            logger.exception(ff)
            continue
    else:
        result = 'not found'
        return result


# To search for a tenant name in a user message.
# always return the name of the species - tenant_12345
def normalize_tenent_name(tenant_name):
    t_name = str(tenant_name)
    # Validating length, number
    if t_name.isdigit() is True and 3 < len(t_name) < 7:
        result = 'tenant_' + str(t_name)
        return result
    # Validating and searching in the message a word "tenant_".
    elif t_name.isdigit() is False:
        result = re.findall('(?=)tenant_\d{4,6}', t_name)
        if result:
            # return only fist entry
            return result[0]
        else:
            return None
    elif t_name.isdigit() is True:
        return None
    else:
        logger.warning("bug: normolize_tenent_name")
        return None


# To search for a server ID in a user message
def normalize_server_id(server_id):
    # Validating length, number
    if len(server_id) < 36:
        pass
    # Validating to the correct structure server ID
    elif len(server_id) >= 36:
        result = re.findall('(\w{8}-)(\w{4}-)(\w{4}-)(\w{4}-)(\w{12})', server_id)
        if result:
            # return only fist entry
            return ''.join(result[0])
        else:
            return None
    else:
        logger.warning("bug: normalize_server_id")
        return None


#normalize new flavor
def normalize_flavor_param(flavor_param):
    # Made list param
    try:
        result = flavor_param.split(',')
    except:
        return None
    # check list, it's have 3 items
    if len(result) == 3 and result[0] in regions and result[1].isdigit() is True and result[2].isdigit() is True:
        return result
    else:
        return None


# bot diagnostic server
def bot_diagnostic(server_id):
    bot_answer = []
    for reg in regions:
        try:
            sess = region_env(reg)
            nova = novaclient.Client(version="2.0", session=sess)
            try:
                url_request = nova.servers.diagnostics(server_id)
                for key, value in url_request[1].items():
                    bot_answer.append(f"<b>{key}</b> : {value}\n")
                return sorted(bot_answer)
            except:
                continue
        except Exception as ff:
            logger.exception(ff)
            continue
    else:
        bot_answer = "Search results: fail"
        return bot_answer


# Show quote in the tenant
def bot_qoute_show(tenant_name):
    bot_answer = []
    txt = ""
    for reg in regions:
        logger.info(reg)
        try:
            sess = region_env(reg)
            keystone = keyclient.Client(session=sess)
            tenant_dict = {t.name: t.id for t in keystone.tenants.list()}
            # looking for a tenant in the DC
            if tenant_dict.get(tenant_name):
                id = tenant_dict.get(tenant_name)
            else:
                continue
            #  get information about tenant resources in nova
            nova = novaclient.Client(version="2.0", session=sess)
            nova_request = nova.quotas.get(id, detail=True)
            # preparing an answer
            for kk, vv in nova_request._info.items():
                if kk=='id':
                    continue
                txt += "<code>" + kk + ":        "
                for res, chis in dict(vv).items():
                    if res=='reserved':
                        continue
                    txt += "[" + res + "=" + str(chis) + "]  "
                txt += "</code>\n"
            bot_answer.append(txt)
            #  get information about tenant resources in cinder
            cinder = cinderclient.Client(version="2", session=sess)
            quota = cinder.quotas.get(id, usage=True)
            quotas_info_dict = cinderutils.unicode_key_value_to_string(quota._info)
            # this is we have dict in dict, for return an answer we need to deleting a key not containing dict
            del quotas_info_dict['id']
            for key, value in quotas_info_dict.items():
                bot_answer.append(f"<b>{key} </b>:      ")
                for res, chis in value.items():
                    if res=='reserved' or res=='allocated':
                        continue
                    else:
                        bot_answer.append(f"[{res} = {chis}]  ")
                bot_answer.append(f"\n")
            return bot_answer
        except Exception as ff:
            logger.exception(ff)
            continue
    else:
        bot_answer = "Search results: fail"
        return bot_answer

