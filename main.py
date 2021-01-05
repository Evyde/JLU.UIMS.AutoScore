import json
import logging
import time
from hashlib import md5
from logging import *
from urllib import parse

import muggle_ocr
import requests

import MessageSender

username = ""
password = ""
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'Origin': 'https://uims.jlu.edu.cn',
    'Host': 'uims.jlu.edu.cn',
    'referer': 'https://uims.jlu.edu.cn/ntms/userLogin.jsp?reason=logout',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Connection': 'Keep-Alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Upgrade-Insecure-Requests': '1'
}
jsonHeaders = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
    'Origin': 'https://uims.jlu.edu.cn',
    'Host': 'uims.jlu.edu.cn',
    'referer': 'https://uims.jlu.edu.cn/ntms/userLogin.jsp?reason=logout',
    'Content-Type': 'application/json',
    'Connection': 'Keep-Alive',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Upgrade-Insecure-Requests': '1'
}
maxPredict = 5
delayTime = 5 * 60
m = MessageSender.MessageSender("bark")
m.config({"apikey": ""})


def getCaptchaCode(img):
    global sdk
    try:
        captchas = []
        for i in range(5):
            captchas.append(sdk.predict(image_bytes=img)[0:4])
        captchasDict = {}
        for key in captchas:
            captchasDict[key] = captchasDict.get(key, 0) + 1
        captchasDictOrder = sorted(captchasDict.items(), key=lambda x: x[1], reverse=True)
        return int(captchasDictOrder[0][0])
    except:
        return getCaptchaCode(img)


def login(username, password, times):
    global s
    if times >= 20:
        error("重试次数过多！可能是代码或网络出现问题，退出！")
        quit()
    s.headers.update(headers)
    a = s.get("https://uims.jlu.edu.cn/ntms/open/get-captcha-image.do?s=1").content
    captchaCode = getCaptchaCode(a)
    passwordMD5 = md5(('UIMS' + username + password).encode('utf-8')).hexdigest()
    loginData = {
        'username': username,
        'password': passwordMD5,
        'mousePath': "",
        'vcode': str(captchaCode)
    }
    loginData = parse.urlencode(loginData).encode('utf-8')
    res = s.post(url="https://uims.jlu.edu.cn/ntms/j_spring_security_check", data=loginData).content.decode()
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
    res = s.post(url="https://uims.jlu.edu.cn/ntms/service/res.do", data=json.dumps(postData)).content.decode()
    rtnData = json.loads(res)
    debug(rtnData)
    return rtnData


def getScoreStateDict(idName, courseID):
    global s
    s.headers.update(jsonHeaders)
    url = "https://uims.jlu.edu.cn/ntms/score/course-score-stat.do"
    postData = {
        idName: courseID
    }
    rtnData = json.loads(s.post(url=url, data=json.dumps(postData)).content.decode())
    debug(rtnData)
    return rtnData


logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
warning('Started.')

sdk = muggle_ocr.SDK(model_type=muggle_ocr.ModelType.Captcha)
s = requests.session()
try:
    with open('.reachee_uims_autoscore', 'r') as f:
        posted = eval(f.read())
    if not isinstance(posted, list): raise Exception
except:
    error('无历史记录！')
    posted = []
while True:
    try:
        asId = getScoreDict()['id']
        posts = getScoreDict()['value']
        for pid in posts:
            if pid in posted: continue
            info("新成绩！{}".format(pid))
            info("获取排名...")
            ranks = getScoreStateDict(asId, pid[asId])['items']
            sendData = {
                "title": "{} 成绩已出！".format(pid['course']['courName']),
                "content": "{}分,绩点{}.班级{}占{},{}占{},{}占{},{}占{},{}占{}".format(
                    pid['score'], pid['gpoint'], ranks[0]['label'], round(float(ranks[0]['percent']), 1),
                    ranks[1]['label'], round(float(ranks[1]['percent']), 1),
                    ranks[2]['label'], round(float(ranks[2]['percent']), 1),
                    ranks[3]['label'], round(float(ranks[3]['percent']), 1),
                    ranks[4]['label'], round(float(ranks[4]['percent']), 1),
                )
            }
            m.send(sendData)
            info(sendData)
            posted.append(pid)
            try:
                with open('.reachee_uims_autoscore', 'w') as f:
                    f.write(repr(posted))
            except:
                error('无法写入文件！')
        time.sleep(delayTime)

    except:
        login(username, password, 0)
        continue
