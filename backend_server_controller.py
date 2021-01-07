import requests
import json
import uuid
import random
import string
import time
import socket
headers = {
        'Content-Type': 'text/html;charset=utf-8',
        'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
    }
# Url
base_url = "http://inbs.tizihu.space:65432"
username = 'admin'
password = 'admin'

def is_port_used(ip, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ip, port))
        return True
    except OSError:
        return False
    finally:
        s.close()

# login and get cookies
def getCookies(username, password):
    url_login =base_url+"/login"
    admin={"username": username, "password": password}
    res = requests.post(url_login, data=admin)
    v2_cookies = res.cookies
    return v2_cookies

def getInbounds():
    url_inbounds = base_url + "/v2ray/inbounds"
    v2_cookies = getCookies(username, password)
    res = requests.get(url_inbounds, cookies=v2_cookies)
    res = res.json()
    return res

def getUserIndex(remark):
    inbonds = getInbounds()
    for inbond in inbonds:
        if inbond['remark']==remark:
            index = inbond['id']
            return index

def getServerStatus():
    url_ServerStatus = base_url + "/server/status"
    v2_cookies=getCookies(username, password)
    res = requests.get(url_ServerStatus, cookies=v2_cookies)
    res=res.json()
    return res


def deleteUser(remark):
    index=getUserIndex(remark)
    url_del = base_url+"/v2ray/inbound/del/"+str(index)
    v2_cookies=getCookies(username, password)
    res = requests.post(url_del, cookies=v2_cookies)

def clearAllUser():
    inbonds=getInbounds()
    for inbond in inbonds:
        remark = inbond['remark']
        deleteUser(remark)

def updateUserEnable(remark,enable):
    inbonds=getInbounds()
    for inbond in inbonds:
        if inbond['remark']==remark:
            inb = inbond
            inb['enable']=enable
            index = inb['id']
    inb = json.dumps(inb, separators=(',', ':'))
    url_update = base_url + "/v2ray/inbound/update/" + str(index)
    v2_cookies = getCookies(username, password)
    res = requests.post(url_update, cookies=v2_cookies,data=inb)

def userExistCheck(remark,port):
    inbounds = getInbounds()
    for inbs in inbounds:
        if ((inbs['remark']==remark) | (inbs['port']==port)):
            return True
    else:
        return False

def addUser_tls(port,id,alterID,serverName,certificateFile,keyFile,remark):
    url_add = base_url+"/v2ray/inbound/add"
    settings={"clients":[{"id":id,"alterId":alterID}],"disableInsecureEncryption":True}
    settings=json.dumps(settings,separators=(',',':'))
    stream_settings={"network":"ws","security":"tls","tlsSettings":{"serverName":serverName,"allowInsecure":True,"certificates":[{"certificateFile":certificateFile,"keyFile":keyFile}]},"wsSettings":{"path":"/","headers":{}}}
    stream_settings=json.dumps(stream_settings,separators=(',',':'))
    sniffing={"destOverride":["http","tls"],"enabled":True}
    sniffing=json.dumps(sniffing,separators=(',',':'))
    data_tls = {"port":port,
                "listen":"0.0.0.0",
                "protocol":"vmess",
                "settings":settings,
                "stream_settings":stream_settings,
                "sniffing":sniffing,
                "remark":remark
    }
    v2_cookies = getCookies(username, password)
    res = requests.post(url_add,data=data_tls,cookies=v2_cookies)
    return res




if __name__ == '__main__':
    id=str(uuid.uuid1())
    alterID = 2
    serverName = "inbs.tizihu.space"
    certificateFile = "/etc/ssl/ray.akbibi.top_chain.crt"
    keyFile = "/etc/ssl/ray.akbibi.top_key.key"
    port=3457
    remark = ''.join(random.sample(string.ascii_letters + string.digits, 16))
    portExist=userExistCheck("", port)
    portUsed=is_port_used('inbs.tizihu.space',port)
    remarkExist=userExistCheck(remark,0)
    if not portExist:
        if not portUsed:
            if not remarkExist:
                    res = addUser_tls(port, id, alterID, serverName, certificateFile, keyFile, remark)
                    print(res.text)
        serverStatus = getServerStatus()
        error_msg = serverStatus['v2']['error_msg']
        if error_msg !='':
               print(error_msg)