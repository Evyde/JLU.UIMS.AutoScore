import json
import logging
import random
import time
from hashlib import md5
from logging import *
from urllib import parse
from Crypto.Cipher import AES

import muggle_ocr
import requests
import urllib3
import configparser

import MessageSender

cfg = configparser.ConfigParser()
cfg.read("config.ini")

useVpn = False
VPNUsername = ""
VPNPassword = ""
username = ""
password = ""
baseURL = "https://uims.jlu.edu.cn/"
baseURL_VPN = "https://vpns.jlu.edu.cn/https/77726476706e69737468656265737421e5fe4c8f693a6445300d8db9d6562d/"
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 " \
     "Safari/537.36"
maxPredict = 5
delayTime = 5 * 60
pushMethod = "bark"
pushConfig = {"apikey": ""}
key = "wrdvpnisawesome!"
iv = "wrdvpnisawesome!"
BLOCK_SIZE = 16  # Bytes
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * '\0'

if "Default" in cfg and "API" in cfg:
    useVpn = cfg.getboolean("Default", "UseVPN")
    VPNUsername = cfg.get("Default", "VPNUsername")
    VPNPassword = cfg.get("Default", "VPNPassword")
    username = cfg.get("Default", "UserName")
    password = cfg.get("Default", "Password")
    baseURL = cfg.get("API", "BaseURL")
    baseURL_VPN = cfg.get("API", "BaseURL_VPN")
    UA = cfg.get("Default", "UA")
    maxPredict = cfg.getint("Default", "MaxPredict")
    delayTime = cfg.getint("Default", "DelayTime")
    pushMethod = cfg.get("Default", "PushMethod")
    pushConfig = json.loads(cfg.get("Default", "PushConfig"))
    key = cfg.get("API", "Key")
    iv = cfg.get("API", "Key")

m = MessageSender.MessageSender(pushMethod)
m.config(pushConfig)

headers = {
    'User-Agent': UA,
    'Content-Type': 'application/x-www-form-urlencoded'
}
jsonHeaders = {
    'User-Agent': UA,
    'Content-Type': 'application/json'
}


def aesEncrypt(key, iv, data):
    key = key.encode('utf8')
    iv = iv.encode('utf-8')
    # data = pad(data)
    cipher = AES.new(key, AES.MODE_OFB, iv=iv)
    result = cipher.encrypt(data.encode('utf-8'))
    enctext = result.hex()
    return iv.hex() + enctext


def VPNLogin(vusr, vpwd):
    global s, baseURL, baseURL_VPN, headers, jsonHeaders, key, iv
    baseURL = baseURL_VPN
    s.headers.update(headers)
    s.verify = False
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    warning("VPN登录！")
    postPayload = {
        'auth_type': 'local',
        'sms_code': '',
        'username': vusr,
        'password': vpwd # aesEncrypt(key, iv, vpwd)
    }
    s.post(cfg.get("API", "VPNLogin"), data=postPayload)
    info("VPN登录完成")


def getCaptchaCode(img):
    global sdk
    info("开始识别验证码")
    try:
        captchas = []
        for i in range(5):
            captchas.append(sdk.predict(image_bytes=img)[0:4])
        captchasDict = {}
        for key in captchas:
            captchasDict[key] = captchasDict.get(key, 0) + 1
        captchasDictOrder = sorted(captchasDict.items(), key=lambda x: x[1], reverse=True)
        return captchasDictOrder[0][0]
    except:
        return getCaptchaCode(img)


def login(username, password, times):
    global s, VPNUsername, VPNPassword, cfg
    if useVpn:
        VPNLogin(VPNUsername, VPNPassword)
    if times >= 10:
        error("重试次数过多！可能是代码或网络出现问题，退出！")
        quit()
    s.headers.update(headers)
    info("用户 {} 开始登录 - 第 {} 次".format(username, times + 1))
    try:
        a = s.get("{}{}?s={}".format(baseURL, cfg.get("API", "LoginCaptcha"), round(random.uniform(0, 1), 16)),
                  timeout=2).content
        debug(a)
    except:
        login(username, password, times + 1)
    else:
        captchaCode = getCaptchaCode(a)
        info("验证码：{}".format(captchaCode))
        passwordMD5 = md5(('UIMS' + username + password).encode('utf-8')).hexdigest()
        loginData = {
            'username': username,
            'password': passwordMD5,
            'mousePath': "",
            'vcode': str(captchaCode)
        }
        loginData = parse.urlencode(loginData).encode('utf-8')
        res = s.post(url="{}{}".format(baseURL, cfg.get("API", "Login")), data=loginData).content.decode()
        if '登录错误' in res:
            error("登录错误，重试！")
            login(username, password, times + 1)
        else:
            warning("登录成功！")
            return


def getScoreDict():
    global s
    s.headers.update(jsonHeaders)
    postData = {
        "tag": "archiveScore@queryCourseScore",
        "branch": "latest"
    }
    res = s.post(url="{}{}".format(baseURL, cfg.get("API", "Score")), data=json.dumps(postData)).content.decode()
    rtnData = json.loads(res)
    debug(rtnData)
    return rtnData


def getScoreStateDict(idName, courseID):
    global s
    s.headers.update(jsonHeaders)
    url = "{}{}".format(baseURL, cfg.get("API", "ScoreState"))
    postData = {
        idName: courseID
    }
    rtnData = json.loads(s.post(url=url, data=json.dumps(postData)).content.decode())
    debug(rtnData)
    return rtnData


logging.basicConfig(level=cfg.get("Default", "Log"), format='%(asctime)s %(levelname)s %(message)s')
warning('开始。')
sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
s = requests.session()
firstLogin = True
try:
    with open(cfg.get("API", "Prefix"), 'r') as f:
        posted = eval(f.read())
    if not isinstance(posted, list): raise Exception
except:
    error('无历史记录！')
    posted = []
while True:
    try:
        if firstLogin:
            warning("首次登录！")
            firstLogin = False
            raise Exception()
        info("获取成绩...")
        scoreDict = getScoreDict()
        asId = scoreDict['id']
        posts = scoreDict['value']
        for pid in posts:
            if pid in posted: continue
            warning("新成绩！{} - {}分".format(pid['course']['courName'], pid['score']))
            info("获取排名...")
            ranks = getScoreStateDict(asId, pid[asId])['items']
            sendData = {
                "title": "{} 成绩已出！".format(pid['course']['courName']),
                "content": "{}分,绩点{}.班级{}占{}%,{}占{}%,{}占{}%,{}占{}%,{}占{}%".format(
                    pid['score'], pid['gpoint'], ranks[0]['label'], round(float(ranks[0]['percent']), 1),
                    ranks[1]['label'], round(float(ranks[1]['percent']), 1),
                    ranks[2]['label'], round(float(ranks[2]['percent']), 1),
                    ranks[3]['label'], round(float(ranks[3]['percent']), 1),
                    ranks[4]['label'], round(float(ranks[4]['percent']), 1),
                )
            }
            info("推送通知 - {}".format(m.send(sendData)))
            posted.append(pid)
            try:
                info("写入文件")
                with open(cfg.get("API", "Prefix"), 'w') as f:
                    f.write(repr(posted))
                    info("写入成功")
            except:
                error('无法写入文件！')
        else:
            info("没有新成绩")
        info("休息 {} 秒".format(delayTime))
        time.sleep(delayTime)

    except:
        warning("重新登录")
        login(username, password, 0)
        continue
